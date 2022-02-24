# animeshorts

[animeshorts](http://animeshorts.pythonanywhere.com/) is a website I made, a successor to [this post](https://redd.it/5nsjw5) I made on /r/anime in 2017.

The code to generate the webpages is written in python3, using [yattag](http://www.yattag.org/) to generate static Bootstrap HTML. `./generate` generates a static html site at `./output`

Feel free to make a [PR](https://github.com/seanbreckenridge/animeshorts/pulls) if you wish to contribute in general. Final say on what goes on the list is up to me, but I'm glad to take suggestions.

Served with `nginx` like:

```
  location /animeshorts {
    if ($request_uri ~ ^/(.*)\.html$) {
      return 302 /$1;
    }
    try_files $uri $uri.html $uri/ =404;
  }
```

to remove the `.html` from the URI.

The `check_links` script checks the external URLs (all the videos/databases) this links to to make sure they're all still valid.
