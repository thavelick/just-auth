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
    ./just-auth.py --port 8486
    ```

## Configuration
For now, there isn't really configuration.
You just have to edit the constants PASSWORD, SALT and PROXY_URL in the script.
It will only work with http, not https.
The idea here is you'd put this between a reverse-proxying web server like nginx and your application.
It contains a simple login form, and sets a cookie to track logged in status

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