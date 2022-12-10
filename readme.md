# Inofficial Citybike Vienna API

**This project is deprecated as citybike vienna stopped operations**

This projects provides an inofficial API to interact with the Citybike System in Vienna.

Check out the docs at: <https://citybike-api.herokuapp.com/docs>

Its goal is to provide a simple and usable interface for every action you can take on the official website (<https://citybikewien.at/>).
It mostly works by parsing the website and mimicking real interaction on it. Which is why it is **very slow**.
For the real time station info the official API is converted to JSON and served with a few utility functions. (such as search by id or coordinates)

**USE AT YOUR OWN RISK**
Some actions require you to log in with your Citybike account (see below).
While this application doesn't save your password, I take no responsibility for anything that might happen with your account.

## Login

In order to perform some actions you need to log into your Citybike account.
The authentication is implemented so that the session key for the Citybike website is passed as a Bearer token in the HTTP Headers.

**Be warned that you should never send your login info or session cookies to a third party site.**

**DON'T USE THIS API, unless you know the risks and trust me and the [source code](https://github.com/bernikr/citybike-api) enough to not steal your data**

**I REPEAT, ABSOLUTELY DON'T SEND YOUR LOGIN INFO OR SESSION KEY**

If you still want to use this API this is how to log in:

There are two possible ways to obtain a session token:

### 1) Via the Citybike Website

In your browser log into <https://citybikewien.at/>.
Go to the cookies and copy the **content** of the cookie that is named `a3990c06031454fe8851126e4477ea83`.
This is your Bearer token that needs to be passed to the API at every request that requires it.

### 2) Via the API

There is the `/account/token` endpoint that takes your username and password and returns a session token.
