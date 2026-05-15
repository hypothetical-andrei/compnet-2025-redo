### Introducere: Reverse Proxy si Load Balancing in Arhitecturi Distribuite

### Obiectivele acestui stagiu

La finalul acestei sectiuni, studentii vor intelege:

* ce este un reverse proxy si cum difera de un forward proxy
* de ce este folosit Nginx ca reverse proxy in arhitecturi moderne
* ce inseamna load balancing si unde se aplica in pipeline-ul HTTP
* cum arata fluxul request-response printr-un proxy
* ce rol va avea load balancer-ul custom implementat ulterior

### 1. Ce este un Reverse Proxy?

Un reverse proxy este un server aflat intre client si un set de servere backend. El primeste request-urile de la clienti si le redirectioneaza catre unul sau mai multe servicii interne.

```text
Client -> Reverse Proxy -> Backend 1
                       -> Backend 2
                       -> Backend 3
```

Spre deosebire de un forward proxy, care reprezinta clientul in exterior, un reverse proxy reprezinta serviciile backend.

### 2. De ce folosim Nginx ca reverse proxy?

Nginx este folosit in multe aplicatii moderne pentru ca ofera:

* terminare TLS
* load balancing
* buffering si caching
* optimizari pentru HTTP
* gestionarea eficienta a conexiunilor concurente
* izolare a backend-urilor

In acest seminar pornim cu Nginx ca exemplu de proxy industrial, dupa care implementam un load balancer propriu, mult mai simplu, dar util pentru intelegerea mecanismelor interne.

### 3. Ce este load balancing?

Load balancing este procesul prin care cererile sunt distribuite intre mai multe instante backend.

Exemplu cu 3 backend-uri:

```text
Request 1 -> web1
Request 2 -> web2
Request 3 -> web3
Request 4 -> web1
```

Acesta este algoritmul round-robin.

### 4. Service discovery in Docker Compose

In aceasta arhitectura, Nginx nu comunica prin `localhost` cu backend-urile. Docker Compose creeaza automat o retea interna si un DNS intern.

Astfel, numele serviciilor devin hostnames valide:

* `web1`
* `web2`
* `web3`

Exemplu in Nginx:

```nginx
upstream backend_pool {
    server web1:8000;
    server web2:8000;
    server web3:8000;
}
```

Aici `web1`, `web2`, `web3` nu sunt adrese IP statice. Sunt nume DNS interne oferite de Docker Compose.

### 5. Structura generala a seminarului

Seminarul are doua parti:

* Etapa A: Nginx ca reverse proxy si load balancer
* Etapa B: load balancer custom in Python

In prima parte observam un instrument de productie. In a doua parte reconstruim o versiune educationala pentru a intelege ce se intampla in interior.

### 6. Sarcina studentului

Creati fisierul:

```text
reverse_proxy_intro_findings.txt
```

Raspundeti la urmatoarele intrebari:

1. Care este diferenta dintre reverse proxy si forward proxy?
2. De ce este un reverse proxy util pentru microservicii?
3. Desenati o diagrama ASCII cu un reverse proxy si 3 backend-uri.
4. Care sunt doua avantaje concrete ale load balancing-ului?
