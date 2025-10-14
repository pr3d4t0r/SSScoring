# Dockerized SSScore

## Build instructions

The SSScore/SSScoring policy is that the Docker image and the package versions
must match.

1. Ensure that the Docker version uses the correct package version by checking
   the contents of `dockerimageversion.txt`
2. `make image`
3. `make push`

This creates a new image, tags it to the Docker Hub repository specified in
`dockerimagename.txt` and uploads it.  Modify this file to push the image to a
different repository.


### Build from the main `Makefile`

From the project directory:

```sh
make dockerize
```

This ensures matching of the package and image versions, builds, and pushes the
image to Docker Hub.

---
## Running the Docker image

To run a SSScore container execute:

```sh
docker compose up
```

The `docker-compose.yaml` file shows the basic app configuration.  If running in
the local system, point the browser to `https://localhost:8501` to access the
application.

The container will try to allocate 4 CPUs and 4 GB of RAM at the start.  These
seem to be more than enough resources for even large numbers of SMD track files.


---
## Running the Docker image in a server

1. Ngnix is the SSScoring project preferred reverse SSL proxy
1. Configuring the SSL proxy is outside of the scope of this document

Streamlit applications use Websocket and require extra configuration in the
`nginx.conf` file.  This snippet shows the exact configuration parameters
required to ensure smooth operation:

```ngnix
    server {
        listen       443 ssl;
        server_name  speedskydiving.app;
        access_log   /var/log/nginx/speedskydiving_app.access.log  main;
        error_log    /var/log/nginx/speedskydiving_app.error.log;

        ssl_certificate_key         /etc/nginx/ssl/private/speedskydiving_app.key;
        ssl_certificate             /etc/nginx/ssl/certs/speedskydiving_app.ca-bundle.crt;
        ssl_session_timeout         5m;
        ssl_ciphers                 "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA256:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:HIGH:!aNULL:!eNULL:!EXPORT:!DES:!MD5:!PSK:!RC4";
        ssl_protocols               TLSv1.2 TLSv1.3;
        ssl_session_cache            shared:SSL:10m;
        ssl_stapling                on;
        ssl_stapling_verify         on;
        ssl_prefer_server_ciphers   on;

        location / {
            proxy_pass          http://192.168.0.240:8908;
            proxy_set_header    Host $host;
            proxy_set_header    X-Real-IP $remote_addr;
            proxy_set_header    X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header    X-Forwarded-Proto $scheme;
            # Begin Streamlint-specific
            proxy_http_version  1.1;
            proxy_set_header    Upgrade $http_upgrade;
            proxy_set_header    Connection "upgrade";
            # End Streamlint-specific
        }
    }
```

Pay particular attention to the `location` directive and configuration.  In this
example:

- The SSScore container opens port 8908, not 8501, because there are other
  containers running behind the same SSL reverse proxy and the hosting
  organization defined the ports range 8900 - 8999 for services.
- Include all the headers
- Look at the Streamlit-specific headers and configuration and ensure those
  are present in your configuration.

The application will start and behave the same way as when running off
localhost:8501 if all the headers are present and the SSL configuration is
correct.

