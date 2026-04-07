class Footer extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.innerHTML = `
            <footer class="position-relative">
                <div class="container">
                    <div class="row">

                        <div class="col-lg-3 mt-4 ml-auto">
                            <ul class="list-unstyled footer-link">
                                <li><a href="https://www.instagram.com/akku.chakku/">3instagram</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-3 mt-4 ml-auto">
                            <ul class="list-unstyled footer-link">
                                <li><a href="https://musescore.com/user/34099211">music</a></li>
                            </ul>
                        </div>
                        <div class="col-lg-3 mt-4 ml-auto">
                            <ul class="list-unstyled footer-link">
                                <!-- Please note.You are not allowed to remove credit link.Please respect that.-->
                                <li><a href="https://themewagon.com/themes/free-bootstrap-4-html5-responsive-portfolio-website-template-art-studio/">site template</a></li>
                            </ul>
                        </div>
                    </div>
                    <!--/.row-->
                </div>
                <!--/.container-->
            </footer>
        `;
    }
}

