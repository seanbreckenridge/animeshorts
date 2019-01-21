# animeshorts

[animeshorts](http://animeshorts.pythonanywhere.com/) is a website I made, a successor to [this post](https://redd.it/5nsjw5) I made on /r/anime in 2016.

The code to generate the webpages is written in python3, using [yattag](http://www.yattag.org/) to [generate Bootstrap HTML templates](https://github.com/purplepinapples/animeshorts/tree/master/site/templates) to be rendered by [Flask](http://flask.pocoo.org/).

Currently, the site only links to MAL, but I left the [yaml](https://github.com/purplepinapples/animeshorts/blob/master/site/html_generators/list_sources.yaml#L4) and [python](https://github.com/purplepinapples/animeshorts/blob/master/site/html_generators/generate_list.py#L288) files relatively open, so if someone wants to contribute (i.e. add AniList ([API example](https://gist.github.com/purplepinapples/5dc60f15f2837bf1cea71b089cfeaa0a))), [create an issue](https://github.com/purplepinapples/animeshorts/issues) and I'm happy to work with ya.
