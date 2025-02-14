// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBTH-2zZR6ykmvhOsczuhQEIKsIB9o9ays",
  authDomain: "vytalgym.firebaseapp.com",
  projectId: "vytalgym",
  storageBucket: "vytalgym.firebasestorage.app",
  messagingSenderId: "861992809821",
  appId: "1:861992809821:web:7295720a697ba5670d64b4",
  measurementId: "G-7BR5SSGV0F"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);