# Mindustry Logic documentation

A [Github Page](https://yrueii.github.io/MlogDocs) containing documentations of [Mindustry](https://mindustrygame.github.io/) Logic
## About This Site

This site serves as a comprehensive resource for Mindustry Logic, providing users with detailed documentation, examples, and guides to enhance their understanding and usage of the Mindustry Logic scripting language. 

### Getting Help

If you encounter issues or have questions, feel free to reach out through the GitHub repository's issues page or join the community discussions to seek assistance from fellow users and contributors.


## Building a local server
For contribution you will need a local server to host the site.  
At its core it is just a HTML file with links to other files
. Since the documentation uses YAML files and external scripts, you'll need to run it through a local server rather than opening the file directly.

### Steps to run locally:

1. **Clone or download the repository** to your local machine
2. **Install a local server** (choose one):
    - **Visual Studio Code**: Use the Live Preview extension to serve your files locally.
    - **Python 3**: `python -m http.server 8000`
    - **Python 2**: `python -m SimpleHTTPServer 8000`
    - **Node.js**: `npx http-server`
    - **PHP**: `php -S localhost:8000`
3. **Navigate to the repository directory** in your terminal
4. **Start the server** using one of the commands above
5. **Open your browser** and go to `http://localhost:8000`

**Note:** Simply opening `index.html` locally won't work because the site uses `fetch()` to load YAML files, which requires HTTP. Browsers block local file access for security reasons, so a local server is necessary.

## Translation Contribution
To contribute a translation please read [Translating](TRANSLATING.md)