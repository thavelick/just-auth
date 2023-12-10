# Just Auth
A minimal reverse proxy server with cookie based authentication.

## Installation and Usage
1. Clone the repository
    ```
    git clone https://github.com/thavelick/just-auth
    ```
2. Run the server
    ```
    cd just-auth
    ./just-auth.py
    ```

## Setup

The idea here is you'd put this between a reverse-proxy capable web server like nginx and your application.
It contains a simple login form, and sets a cookie to track logged in status.
The url you proxy to needs to be http, not https.
It is expected that the web server in front of Just Auth will provide https.

### Environment Variables

| Variable | Description | Default |
| -------- | ----------- | ------- |
| PASSWORD | The password to use for authentication | super secret password |
| SALT | The salt to use for hashing the password | pretty secret salt |
| PROXY_TO_URL | The url to proxy to | http://localhost:8000 |
| PORT | The port to listen on | 8486

## FAQ
Q. Why not just use http authentication?

A. Many browsers, particularly on mobile, don't keep credentials for very long at all.
   Also, if another site, (such as my own Just Bangs!) redirects to a site using http authentication,
   the browser can tend to hang waiting on the credentials, requiring a refresh which is annoying.
   Just Auth will just remember the auth token until it is removed

Q. Should I use this in production?

A. No, although it's secure to my limited knowledge and purposes, it's not very robust at all.
   It certainly hasn't had any kind of security review.
   Also, it's based on python's http.server module which the docs warn against using in production.