import time
import dns.resolver
import dns.exception

RESOLVER_IP = "172.28.0.11"
QUERY_NAME = "www.example.test"
QUERY_TYPE = "A"


def q():
    r = dns.resolver.Resolver(configure=False)
    r.nameservers = [RESOLVER_IP]

    try:
        ans = r.resolve(QUERY_NAME, QUERY_TYPE)
        print(
            "A =",
            [a.to_text() for a in ans],
            "TTL =",
            ans.rrset.ttl,
            flush=True,
        )
    except dns.exception.DNSException as err:
        print(f"DNS error: {err}", flush=True)


if __name__ == "__main__":
    for i in range(5):
        q()
        time.sleep(2)