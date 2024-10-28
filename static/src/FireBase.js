<script type="module">
  // Import the functions you need from the SDKs you need
  import { initializeApp } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/11.0.1/firebase-analytics.js";
  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries

  // Your web app's Firebase configuration
  // For Firebase JS SDK v7.20.0 and later, measurementId is optional
  const firebaseConfig = {
    apiKey: "AIzaSyA7JsUVH4mbVN0mjljVeYGkBhSiART8PD4",
    authDomain: "endpoints-c1050.firebaseapp.com",
    projectId: "endpoints-c1050",
    storageBucket: "endpoints-c1050.appspot.com",
    messagingSenderId: "865827232151",
    appId: "1:865827232151:web:fb753735f775de4d5c8cd2",
    measurementId: "G-P6RRJTR2YG"
  };

  // Initialize Firebase
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
</script>