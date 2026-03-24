import ipaddress
import math
import sys


def needed_prefix(hosts_needed: int) -> int:
    size = hosts_needed + 2
    bits = math.ceil(math.log2(size))
    return 32 - bits


def split_once(net: ipaddress.IPv4Network):
    subs = list(net.subnets(prefixlen_diff=1))
    return subs[0], subs[1]


def path_from_base(base: ipaddress.IPv4Network, target: ipaddress.IPv4Network):
    """
    Return the sequence of recursive splits from base to target.
    Each element:
      (parent, left_child, right_child, chosen_child, chosen_bit)
    where chosen_bit is '0' for left and '1' for right.
    """
    if not target.subnet_of(base):
        raise ValueError(f"{target} is not inside {base}")

    path = []
    current = base

    while current.prefixlen < target.prefixlen:
        left, right = split_once(current)

        if target.subnet_of(left):
            chosen = left
            bit = "0"
        elif target.subnet_of(right):
            chosen = right
            bit = "1"
        else:
            raise ValueError(f"Could not descend from {current} toward {target}")

        path.append((current, left, right, chosen, bit))
        current = chosen

    if current != target:
        raise ValueError(f"Reached {current}, expected {target}")

    return path


def bits_relative_to_base(base: ipaddress.IPv4Network, target: ipaddress.IPv4Network) -> str:
    """
    Returns the additional prefix bits used to descend from base to target.
    Example: base /24 to target /27 may return '110'
    """
    path = path_from_base(base, target)
    return "".join(bit for _, _, _, _, bit in path)


def dotted_binary(addr: ipaddress.IPv4Address) -> str:
    return ".".join(f"{octet:08b}" for octet in addr.packed)


def print_prefix_bits(base: ipaddress.IPv4Network, target: ipaddress.IPv4Network, indent="    "):
    base_bits = format(int(base.network_address), "032b")
    target_bits = format(int(target.network_address), "032b")

    common = base.prefixlen
    extra = target.prefixlen - base.prefixlen

    common_part = base_bits[:common]
    chosen_part = target_bits[common:common + extra]
    rest_part = target_bits[common + extra:]

    print(f"{indent}Base prefix bits   : {common_part}")
    if extra > 0:
        print(f"{indent}Chosen subnet bits : {chosen_part}")
    print(f"{indent}Remaining host bits: {rest_part}")


def print_split_path(base: ipaddress.IPv4Network, target: ipaddress.IPv4Network, indent="    "):
    path = path_from_base(base, target)

    print(f"{indent}Tree path from {base} to {target}:")
    if not path:
        print(f"{indent}  {base} (already exact match)")
        return

    bits_so_far = ""
    for level, (parent, left, right, chosen, bit) in enumerate(path):
        side = "left" if bit == "0" else "right"
        bits_so_far += bit

        print(f"{indent}  Step {level + 1}: split {parent}")
        print(f"{indent}    |- {left}   [bit 0]")
        print(f"{indent}    `- {right}   [bit 1]")
        print(f"{indent}    -> choose {side}: {chosen}")
        print(f"{indent}       selected bit: {bit}")
        print(f"{indent}       bits so far : {bits_so_far}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 vlsm_alloc_debug_bits.py <base_network/prefix> <hosts1> <hosts2> ...")
        sys.exit(1)

    base = ipaddress.ip_network(sys.argv[1], strict=True)
    req = [int(x) for x in sys.argv[2:]]
    req_sorted = sorted(req, reverse=True)

    cursor = int(base.network_address)
    end = int(base.broadcast_address)

    allocations = []
    for h in req_sorted:
        pfx = needed_prefix(h)
        block_size = 2 ** (32 - pfx)

        if cursor % block_size != 0:
            old_cursor = cursor
            cursor = ((cursor // block_size) + 1) * block_size
            print(f"[align] Need /{pfx} block for {h} hosts")
            print(f"        Cursor moved from {ipaddress.IPv4Address(old_cursor)} "
                  f"to {ipaddress.IPv4Address(cursor)}")
        else:
            print(f"[align] Need /{pfx} block for {h} hosts")
            print(f"        Cursor already aligned at {ipaddress.IPv4Address(cursor)}")

        net = ipaddress.ip_network((cursor, pfx))
        if int(net.broadcast_address) > end:
            raise ValueError("Insufficient address space for requirements")

        allocations.append((h, net))
        print(f"[alloc] Assigned {net} for requirement {h} hosts")
        print(f"        Range: {net.network_address} -> {net.broadcast_address}")
        print(f"        Relative subnet bits: {bits_relative_to_base(base, net) or '(none)'}")
        cursor = int(net.broadcast_address) + 1
        print(f"        Next cursor: {ipaddress.IPv4Address(cursor)}")
        print()

    print("=" * 72)
    print("Final allocations")
    print("=" * 72)
    print("Base:", base)
    print(f"Base network address in binary: {dotted_binary(base.network_address)}")
    print()

    for h, net in allocations:
        hosts = list(net.hosts())
        usable = len(hosts)
        print(f"- Need {h} hosts -> {net} (usable {usable})")
        print(f"  Network:   {net.network_address}")
        print(f"  Broadcast: {net.broadcast_address}")
        print(f"  Net bits:  {dotted_binary(net.network_address)}")
        print(f"  Subnet bits added after /{base.prefixlen}: {bits_relative_to_base(base, net) or '(none)'}")
        if usable:
            print(f"  Hosts:     {hosts[0]} - {hosts[-1]}")
        print()

    print("=" * 72)
    print("Explanatory VLSM tree with selected bits")
    print("=" * 72)
    print()

    for idx, (h, net) in enumerate(allocations, start=1):
        print(f"[{idx}] Requirement: {h} hosts")
        print(f"    Needed prefix: /{needed_prefix(h)}")
        print(f"    Allocated subnet: {net}")
        print(f"    Relative subnet bits: {bits_relative_to_base(base, net) or '(none)'}")
        print_prefix_bits(base, net)
        print_split_path(base, net)
        print()

    print("=" * 72)
    print("Note")
    print("=" * 72)
    print("- Each split adds one more subnet-selection bit.")
    print("- Bit 0 means choose the left half.")
    print("- Bit 1 means choose the right half.")
    print("- The sequence of chosen bits explains how the subnet is derived from the base block.")


if __name__ == "__main__":
    main()