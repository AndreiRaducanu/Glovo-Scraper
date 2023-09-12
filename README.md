![Tests](https://github.com/AndreiRaducanu/Glovo_App/actions/workflows/tests.yml/badge.svg)
[![MIT License][license-shield]][license-url]
![Last Commit][last-commit-shield]
![GitHub repo size](https://img.shields.io/github/repo-size/AndreiRaducanu/Glovo-Scraper)
![Docker Image Version (latest semver)](https://img.shields.io/docker/v/AndreiRaducanu/Glovo-Scraper)

<br />
<div align="center">
  <h3 align="center">Fast Food App Data Scraper</h3>
  <p align="center">
    Glovo-Scraper is a Python project that scrapes data from a popular fast food app, organizes it based on price and location, and then saves it to both CSV and MongoDB for further analysis. This tool allows you to collect valuable data from your favorite fast food restaurants and perform various analyses on it. Ideal for when you want a good meal but don't want to pay more than necessary.
    <br />
    <br />
    <a href="https://github.com/AndreiRaducanu/Glovo-Scraper">View Demo</a>
    ·
    <a href="https://github.com/AndreiRaducanu/Glovo-Scraper/issues">Report Bug</a>
    ·
    <a href="https://github.com/AndreiRaducanu/Glovo-Scraper/issues">Request Feature</a>
  </p>
</div>

<a name="readme-top"></a>
<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project
![Sorted data.png][product-screenshot]

The "Fast Food App Data Scraper" project is a powerful tool designed for efficiently collecting and organizing data from the Glovo application. Whether you're a food enthusiast, a market analyst, or just someone looking for a great meal deal, this project is your go-to solution.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With


[![Docker][Docker.js]][Docker-url]

![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white)

![Beautiful Soup](https://img.shields.io/badge/Beautiful%20Soup-000000?style=for-the-badge&logo=python&logoColor=white)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started
To get a local copy up and running follow these simple example steps.
### Prerequisites

Before you can get started with this project, make sure you have the following prerequisites installed on your system:

1. **Docker**: You'll need Docker to create and manage containers for this project. If you don't have Docker installed, you can download and install it from the official Docker website: [Docker Installation Guide](https://docs.docker.com/get-docker/)

2. **pip (Python Package Manager)**: If you plan to use Python-based components or libraries in this project, ensure that `pip` is installed. `pip` is commonly included with Python installations, but you can upgrade it to the latest version using the following command:

  ```bash
   pip install --upgrade pip
  ```
### Installation
1. Clone the repo:
   ```sh
   git clone https://github.com/AndreiRaducanu/Glovo-Scraper.git
   ```
2. Install the glovo package:
   ```sh
   pip install -e .
   ```

#### Docker installation
You'll need to have docker already installed than follow these steps:
1. Install the latest package (check packages for latest version):
   ```sh
   docker pull ghcr.io/andreiraducanu/glovo-scraper:sha-1c15d79
   ```
2. Run a container using the image:
   ```sh
   docker run -it ghcr.io/andreiraducanu/glovo-scraper:sha-1c15d79
   ```
   Use the "-it" flag since you'll need to input credentials
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Usage

The data stored in the database provides a rich source of information that can be leveraged to perform various queries and analyses. With this data, you can conduct targeted searches to retrieve specific information, such as finding all products with certain keywords or attributes. For instance, if you're interested in identifying all the **burger-related** items in a restaurant's menu, you can perform a query using relevant keywords or filters to retrieve this subset of data.

![MongoDB query.png][burger-screenshot]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Roadmap
- [x] Scrape data from all available restaurants
- [x] Store the aquired data in a database
- [ ] Host a fully-fledged web application
    - [ ] Make it accessible for users in any country using Glovo

See the [open issues](https://github.com/AndreiRaducanu/Glovo-Scraper/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>
 
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. Alternatively, you can open an issue labeled 'enhancement'.
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Andrei Raducanu - [@twitter_handle](https://twitter.com/twitter_handle) - raducanuandrei31@gmail.com

Project Link: [https://github.com/AndreiRaducanu/Glovo-Scraper](https://github.com/AndreiRaducanu/Glovo-Scraper)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments

Resources I've found helpful while building this project:

* [How to use requests for JSON calls](https://requests.readthedocs.io/en/latest/user/quickstart/#json-response-content)
* [Dockerize any application](https://itsromiljain.medium.com/docker-setup-and-dockerize-an-application-5c24a4c8b428)
* [GitHub Emoji Cheat Sheet](https://www.webfx.com/tools/emoji-cheat-sheet/)
* [Badges for GitHub](https://shields.io/)
* [MongoDB Cheat Sheet](https://www.mongodb.com/developer/products/mongodb/cheat-sheet/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[license-url]: https://github.com/AndreiRaducanu/Glovo-Scraper/blob/main/LICENSE.txt
[license-shield]: https://img.shields.io/github/license/AndreiRaducanu/Glovo-Scraper.svg?style=flat
[last-commit-shield]: https://img.shields.io/github/last-commit/AndreiRaducanu/Glovo-Scraper/main?style=flat
[Docker.js]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://docs.docker.com/get-started/overview/
[product-screenshot]: images/sorted_data.PNG
[burger-screenshot]: images/example_db_search.PNG
