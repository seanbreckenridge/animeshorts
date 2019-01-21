from os import path

import yaml
from yattag import Doc, indent

import constants
import generate_navbar

def create_cookie_page():
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
            doc.asis('''<link rel="stylesheet" href="{{url_for('static', filename='bootstrap-4.1.0-dist/css/bootstrap.min.css')}}">''')
            doc.asis('<!-- jQuery -->')
            doc.asis('''<script src="{{url_for('static', filename='jquery-3.3.1.slim.min.js')}}"></script>''')
            with tag('style'):
                doc.asis("""body {
  font-family: 'Lato', sans-serif;
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
  padding-left: 0px;
  padding-right: 0px;
}

p {
  margin-bottom: 0.25rem;
}

""")
            doc.asis("<!-- Fonts -->")
            doc.asis('<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">')
        with tag('body'):
            doc.asis('<!-- navbar -->')
            doc.asis(generate_navbar.navbar(active="")) # dont highlight any item in the navbar
            doc.asis('<!-- compliance note -->')
            with tag('main', klass='container'):
                with tag("div", ('class', "alert alert-dark m-1 mt-0"), ("role", "alert")):
                    with tag('p'):
                        text("This subdomain of pythonanywhere (animeshorts) does not use or store cookies on your system, nor do I store any data about who you are.")
                    with tag('p'):
                        text("However, pythonanywhere does use cookies for a variety of reasons, you can view their policy")
                        with tag('a', href="https://www.pythonanywhere.com/privacy_v2/#cookies"):
                            text("here")
                        text(".")
            doc.asis("<!-- footer -->")
            with tag('footer', ('class', 'bg-dark footer')):
                with tag('div', klass='container center'):
                    with tag("div", klass="row justify-content-center py-2"):
                        with tag("p", klass="mb-0"):
                            text("© PurplePinapples")
                with tag('a', klass="d-none", href=constants.user_link):
                    pass
            doc.asis('<!-- javascript/popper.js -->')
            doc.asis('''<script src="{{url_for('static', filename='bootstrap-4.1.0-dist/js/bootstrap.bundle.min.js')}}"></script>''')
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
    # write out html file
    with open('../templates/cookies.html', 'w') as write_html_file:
        write_html_file.write(create_cookie_page())

if __name__ == "__main__":
    main()
