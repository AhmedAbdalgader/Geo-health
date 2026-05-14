<template>
    <div>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>

        <title>Burundi | Market Analytics</title>
		
		<!-- Load styles of the libraries -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
        
        <!-- Load own styles -->
        <!-- <link rel="stylesheet" href="./styles/index.css" type="text/css"/> -->

        <!-- Define the application icon -->
        <link rel="icon" href="./images/favicon.png" type="image/png">

        <div id="index-bg">
            <div id="index-overlay">
                <main class="d-flex h-100 w-100 justify-content-center align-items-center">
                    <div id="index-info">
                        <h1><strong>Burundi</strong> | Market Analytics</h1>
            
                        <h2>
                            Designed and developed for the MOOC:<br/>
                            <strong>Geo web app building with open-source GIS tools </strong>
                        </h2>

                        <NuxtLink to="/view">
                        <span>Open app</span>
                        </NuxtLink>
                    </div>
                </main>
            </div>
            </div>
    </div>
</template>

<script setup >

</script>

<style scoped>
#index-bg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    background-image: url("./H1.webp");
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center;
}

#index-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    background-color: rgba(255, 255, 255, 0.7);
}

/* •  •  • */

#index-info {
    width: 80%;
    text-align: center;
}

h1 {
    background-color: rgb(84,130,53);
    color: white;
    padding: 3vw 4vw;
    font-size: 5vw;
    clear: both;
}

h2 {
    margin-top: 2vw;
    font-size: 3vw;
    color: black;
}

strong { font-weight: 800; }

a {
    display: inline-block;
    width: auto;
    transition-property: background-color;
    transition-duration: 1000ms;
    background-color: rgb(84,130,53);
    font-size: 2.5vw;
    margin: 5vw 1vw 0 1vw;
    padding: 1.5vw 3vw;
    color: white;
    text-decoration: none;
}

a:hover {
    transition-property: background-color;
    transition-duration: 1000ms;
    background-color: rgb(107, 168, 67);
}
</style>