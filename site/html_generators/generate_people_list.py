from os import path

import yaml
from yattag import Doc, indent
from PIL import Image

import constants
import generate_navbar
from generate_list import join_urls

def image_path(filename):
    return """{{url_for('static', filename='images/people/""" + filename + """')}}"""


def get_ratio_image_from_relative_path(filename):
    """from the html_generators directory, gets the ratio of height/width for an image in the people directory"""
    with Image.open(path.join('../static/images/people/', filename)) as img:
        width, height = img.size
        return "{}%".format(height / width * 100)


def chunk_list(l, chunk_size):
    """Return chunk_size'd lists from the large list."""
    for i in range(0, len(l), chunk_size):
        yield l[i:i+chunk_size]

def create_people_page(sources):
    doc, tag, text = Doc().tagtext()
    doc.asis("<!DOCTYPE html>")
    with tag('html', ("lang", "en")):
        with tag('head'):
            with tag('title'):
                text(constants.SHORT_NAME)
            doc.asis("<!-- Required meta tags -->")
            doc.asis('<meta charset="utf-8">')
            doc.asis('<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">')
            doc.asis('<!-- bootstrap CSS -->')
            doc.asis("""<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">""")
            with tag('style'):
                doc.asis("""body {
  font-family: 'Lato', sans-serif;
}

.image-container {
  position: relative;
  height: 0;
  overflow: hidden;
}

.image-container img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}

.person-link {
  margin-left: .5em;
  white-space: nowrap;
  font-size: 100%;
  text-rendering: auto; /* chrome compliance for small-caps font */
  font-variant: small-caps;
}

.card-text {
  margin-bottom: .5rem !important;
}

@media (max-width:576px) {
  .card-columns {
      column-count: 1;
  }
}

@media (min-width:576px) and (max-width:768px) {
    .card-columns {
      column-count: 2;
    }
}
@media (min-width:768px) and (max-width:992px) {
    .card-columns {
      column-count: 3;
    }
}
@media (min-width:992px) and (max-width:1200px) {
    .card-columns {
      column-count: 4;
    }
}
@media (min-width:1200px) {
    .card-columns {
      column-count: 5;
    }
}

#note {
    background-color: lightgrey;
}

.moveup {
    position: relative;
    top: -0.1rem;

}

.footer {
  color: white;
  position: fixed;
  bottom: 0;
  width: 100%;
}

footer:hover {
  cursor: pointer;
  background-color: #1f2225!important;
}

main.container {
  padding-bottom: 4rem;
}

""")
            doc.asis("<!-- Fonts -->")
            doc.asis('<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">')
        with tag('body'):
            doc.asis('<!-- navbar -->')
            doc.asis(generate_navbar.navbar(active=constants.PEOPLE_TAB))
            doc.asis('<!-- note -->')
            with tag('div', ('class', 'container rounded-bottom py-3 mb-2'), ('id', 'note')):
                with tag('p', ('class', 'text-center mb-0')):
                    text("People I feel are worth checking out:")
            doc.asis('<!-- list -->')
            with tag('main', klass='container'):
                with tag('div', klass='card-columns'):
                    for c in sources:
                        with tag('div', klass='card'):
                            with tag('div', ('class', 'image-container'), ('style', ('padding-bottom:{};'.format(get_ratio_image_from_relative_path(c['image']))))):
                                doc.stag('img', ('class', 'card-img-top img-fluid'), ('src', image_path(c['image'])), alt=c['name'])
                            with tag('div', klass='card-block'):
                                with tag('h4', klass='card-title'):
                                    text(c['name'])
                                with tag('div', klass='card-text'):
                                    for other_link in sorted(list({k : c[k] for k, v in c.items() if k not in ['name', 'image']})):
                                        if other_link == 'mal':
                                            with tag('a', klass='badge badge-pill person-link badge-secondary', href=join_urls('https://myanimelist.net', 'people', c[other_link])):
                                                with tag('span', klass='moveup'):
                                                    text('mal')
                                        elif other_link == 'website':
                                            with tag('a', klass='badge badge-pill person-link badge-secondary movetext', href=c[other_link]):
                                                with tag('span', klass='moveup'):
                                                    text('website')
                                        elif other_link == 'vimeo':
                                            with tag('a', klass='badge badge-pill person-link badge-secondary movetext', href=join_urls('https://vimeo.com', c[other_link])):
                                                with tag('span', klass='moveup'):
                                                    text('vimeo')
                                        elif other_link == 'youtube':
                                            with tag('a', klass='badge badge-pill person-link badge-secondary movetext', href=join_urls('https://www.youtube.com', 'user', c[other_link])):
                                                with tag('span', klass='moveup'):
                                                    text('youtube')
                                        else:
                                            print("Unknown tag: {}".format(other_link))
            doc.asis("<!-- footer -->")
            with tag('footer', ('class', 'bg-dark footer')):
                with tag('div', klass='container center'):
                    with tag("div", klass="row justify-content-center py-2"):
                        with tag("p", klass="mb-0"):
                            text("© PurplePinapples")
                with tag('a', klass="d-none", href=constants.user_link):
                    pass
            doc.asis('<!-- javascript/popper.js -->')
            doc.asis("""<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>""")
            with tag('script'):
                doc.asis("""
// runs when document is loaded:
document.addEventListener('DOMContentLoaded', function() {

  // footer onclick
  let footer = document.querySelector("footer.footer");
  footer.onmouseup = function(a) { // when mouse is released
    if (a.ctrlKey || a.metaKey || a.which == 2) {
      a.preventDefault(); // prevent middle click from opening tab, so it doesnt open twice.
      window.open($(footer).find('a').attr("href"));
    } else {
      window.location = $(footer).find('a').attr("href");
    }
  }

  }, false);
""")
    return indent(doc.getvalue(), indent_text=True)

def main():
    # Read in YAML Sources
    with open(constants.PEOPLE_SOURCES) as yaml_src:
        sources = yaml.load(yaml_src, Loader=yaml.FullLoader)
    # write out html file
    with open('../templates/people.html', 'w') as write_html_file:
        write_html_file.write(create_people_page(sources))

if __name__ == "__main__":
    main()
