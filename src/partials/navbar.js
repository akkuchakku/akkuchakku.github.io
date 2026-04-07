class Nav extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = `
            <head>
                <link rel="stylesheet" href="/src/assets/css/super.css">
            </head>
            <div class="nav-main">
                <div class="container">
                    <nav class="navbar navbar-expand-lg navbar-light">
                        <a class="navbar-brand font-weight-bold" href="/index.html">Portfolio</a>
                        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="collapse navbar-collapse" id="navbarNav">
                            <ul class="navbar-nav">
                                <li class="nav-item">
                                    <a class="nav-link" href="/src/pages/main/jeong.html">Jeong</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link" href="/src/pages/main/cradle.html">Video Essay</a>
                                </li>

                                <li class="nav-item">
                                    <a class="nav-link" href="/src/pages/main/burning.html">Burning - Remake</a>
                                </li>

                                <li class="nav-item">
                                    <a class="nav-link" href="/src/pages/main/literary.html">Literary Work</a>
                                </li>

                                <li class="nav-item">
                                    <a class="nav-link" href="/src/pages/main/toc.html">Tower of Cards</a>
                                </li>
                                
                            </ul>

                            <div class="dropdown">
                                <button class="dropbtn">Other Work</button>
                                <div class="dropdown-content">
                                    <a href="/src/pages/other/ex-sp2.html">SP2 Exercises</a>
                                    <a href="/src/pages/other/ex-sp3.html">SP3 Exercises</a>
                                    <a href="/src/pages/other/draft-sp3.html">SP3 Proof of Concept</a>
                                </div>
                            </div>

                            <ul class="navbar-nav ml-auto">
                            </ul>
                        </div>
                    </nav>
                    <!--end:Nav -->
                </div>
            </div>
        `;
    }
}

customElements.define('nav-component', Nav);