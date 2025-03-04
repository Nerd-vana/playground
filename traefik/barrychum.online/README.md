
## To setup a traefik reverse proxy container

https://technotim.live/posts/traefik-3-docker-certificates/

```
version: "3.8"

services:
  traefik:
    image: traefik:v3.1
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    networks:
      - traefik
    ports:
      - 80:80
      - 443:443
      # - 443:443/tcp # Uncomment if you want HTTP3
      # - 443:443/udp # Uncomment if you want HTTP3
    environment:
      #CF_DNS_API_TOKEN_FILE: /run/secrets/cf_api_token # note using _FILE for docker secrets
      CF_DNS_API_TOKEN: ${CF_DNS_API_TOKEN} # if using .env
      TRAEFIK_DASHBOARD_CREDENTIALS: ${TRAEFIK_DASHBOARD_CREDENTIALS}
    #secrets:
    #  - cf_api_token
    env_file: .env # use .env
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./data/traefik.yml:/traefik.yml:ro
      - ./data/acme.json:/acme.json
      # - ./data/config.yml:/config.yml:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.entrypoints=http"
      - "traefik.http.routers.traefik.rule=Host(`traefik-dashboard.local.britbuzz.uk`)"
      - "traefik.http.middlewares.traefik-auth.basicauth.users=${TRAEFIK_DASHBOARD_CREDENTIALS}"
      - "traefik.http.middlewares.traefik-https-redirect.redirectscheme.scheme=https"
      - "traefik.http.middlewares.sslheader.headers.customrequestheaders.X-Forwarded-Proto=https"
      - "traefik.http.routers.traefik.middlewares=traefik-https-redirect"
      - "traefik.http.routers.traefik-secure.entrypoints=https"
      - "traefik.http.routers.traefik-secure.rule=Host(`traefik-dashboard.local.britbuzz.uk`)"
      - "traefik.http.routers.traefik-secure.middlewares=traefik-auth"
      - "traefik.http.routers.traefik-secure.tls=true"
      - "traefik.http.routers.traefik-secure.tls.certresolver=cloudflare"
      - "traefik.http.routers.traefik-secure.tls.domains[0].main=local.britbuzz.uk"
      - "traefik.http.routers.traefik-secure.tls.domains[0].sans=*.local.britbuzz.uk"
      - "traefik.http.routers.traefik-secure.service=api@internal"

#secrets:
#  cf_api_token:
#    file: ./cf_api_token.txt

networks:
  traefik:
    external: true

```

```
api:
  dashboard: true
  debug: true
entryPoints:
  http:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: https
          scheme: https
  https:
    address: ":443"
serversTransport:
  insecureSkipVerify: true
providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  # file:
  #   filename: /config.yml
certificatesResolvers:
  cloudflare:
    acme:
      email: youremail@email.com
      storage: acme.json
      # caServer: https://acme-v02.api.letsencrypt.org/directory # prod (default)
      caServer: https://acme-staging-v02.api.letsencrypt.org/directory # staging
      dnsChallenge:
        provider: cloudflare
        #disablePropagationCheck: true # uncomment this if you have issues pulling certificates through cloudflare, By setting this flag to true disables the need to wait for the propagation of the TXT record to all authoritative name servers.
        #delayBeforeCheck: 60s # uncomment along with disablePropagationCheck if needed to ensure the TXT record is ready before verification is attempted 
        resolvers:
          - "1.1.1.1:53"
          - "1.0.0.1:53"

```


## To setup a service behind traefik reverse proxy

```
docker run -d \
--label "traefik.http.routers.nginxservice.rule=Host(\`nginxhost.local.britbuzz.uk\`)" \
--label "traefik.http.services.nginxservice.loadbalancer.server.port=8080" \
--label "traefik.http.routers.nginxservice.entrypoints=https" \
--label "traefik.http.routers.nginxservice.tls=true" \
--label "traefik.enable=true" \
--name nginxcontainer --network traefik \
nginxdemos/nginx-hello
```


```
version: '3.8'
services:
  nginx:
    image: nginxdemos/nginx-hello
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.nginx.rule=Host(`nginx.local.britbuzz.uk`)"
      - "traefik.http.routers.nginx.entrypoints=https"
      - "traefik.http.routers.nginx.tls=true"
      - "traefik.http.services.nginx.loadbalancer.server.port=8080"
    networks:
      - traefik

networks:
  traefik:
    external: true

```


## To setup dnsmasq container

### Using docker compose
```
version: '3'

services:
  dnsmasq:
    image: drpsychick/dnsmasq:latest
    container_name: dnsmasq
    ports:
      - "53:53/udp"
      - "53:53/tcp"
    volumes:
      - ./dnsmasq.conf:/etc/dnsmasq.conf
    environment:
      - DNSMASQ_OPTS=--log-facility=-
    cap_add:
      - NET_ADMIN
    restart: unless-stopped
   ```

### Using docker run
```
   docker run -d \
  --name dnsmasq \
  -p 53:53/udp \
  -p 53:53/tcp \
  -v $(pwd)/dnsmasq.conf:/etc/dnsmasq.conf \
  --cap-add=NET_ADMIN \
  --restart unless-stopped \
  drpsychick/dnsmasq:latest
```

### Sample dnsmasq.conf
```
domain=localdomain
server=/example.com/8.8.8.8  

address=/host1/192.168.1.100
address=/host2/192.168.1.101

```

### How to use dig
```
dig <hostname> @<server IP>
```

    

### Configure macOS / Linux to use a specific name server for a domain

You can configure macOS to use a specific DNS server for a particular domain by editing the `/etc/resolver` directory. Here's how you can do it:

1. **Create the `/etc/resolver` directory** (if it doesn't already exist):
   ```sh
   sudo mkdir -p /etc/resolver
   ```

2. **Create a file named after the domain you want to use** (e.g., `example.com`):
   ```sh
   sudo touch /etc/resolver/example.com
   ```

3. **Edit the file to specify the DNS server**:
   ```sh
   sudo nano /etc/resolver/example.com
   ```

4. **Add the following lines to the file**:
   ```
   nameserver [DNS_SERVER_IP]
   ```
   Replace `[DNS_SERVER_IP]` with the IP address of the DNS server you want to use for the specified domain.

5. **Save and exit the file** (in nano, press `Ctrl+X`, then `Y`, then `Enter`).

This will direct DNS queries for `example.com` to the specified DNS server.


## Traefik rule examples

The double pipe (`||`) in Traefik's rules can be used to combine various conditions with a logical "OR". Here are a few examples:

1. **Combining Host and Path**:
   ```yaml
   labels:
     - "traefik.http.routers.my-router.rule=Host(`example.com`) || Path(`/path1`)"
   ```
   - Routes traffic if the host is `example.com` or the path is `/path1`.

2. **Combining Multiple Hosts and Paths**:
   ```yaml
   labels:
     - "traefik.http.routers.my-router.rule=Host(`example.com`) || Host(`another-example.com`) || Path(`/path1`) || Path(`/path2`)"
   ```
   - Routes traffic if the host is `example.com` or `another-example.com`, or if the path is `/path1` or `/path2`.

3. **Combining Host and Header Conditions**:
   ```yaml
   labels:
     - "traefik.http.routers.my-router.rule=Host(`example.com`) || Headers(`X-Custom-Header`, `Value1`)"
   ```
   - Routes traffic if the host is `example.com` or if the header `X-Custom-Header` equals `Value1`.

4. **Combining Path and Query Parameters**:
   ```yaml
   labels:
     - "traefik.http.routers.my-router.rule=Path(`/path1`) || Query(`param=value`)"
   ```
   - Routes traffic if the path is `/path1` or if the query parameter `param` has the value `value`.

5. **Complex Rule with Host, Path, and Methods**:
   ```yaml
   labels:
     - "traefik.http.routers.my-router.rule=Host(`example.com`) || (Path(`/path1`) && Method(`GET`))"
   ```
   - Routes traffic if the host is `example.com` or if the path is `/path1` and the request method is `GET`.

These examples show how the double pipe format allows for flexible and complex routing rules in Traefik.



## Start a cloudflared docker
```
docker run [--network host] cloudflare/cloudflared:2024.6.1 tunnel --no-autoupdate run --token <token>
```

