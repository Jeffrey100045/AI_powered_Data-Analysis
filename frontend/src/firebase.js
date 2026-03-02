import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getStorage } from "firebase/storage";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
    apiKey: (import.meta.env.VITE_FIREBASE_API_KEY || "").trim(),
    authDomain: (import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "").trim(),
    projectId: (import.meta.env.VITE_FIREBASE_PROJECT_ID || "").trim(),
    storageBucket: (import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "").trim(),
    messagingSenderId: (import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "").trim(),
    appId: (import.meta.env.VITE_FIREBASE_APP_ID || "").trim(),
    measurementId: (import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "").trim()
};

console.log("Firebase Init Attempt. Key length:", firebaseConfig.apiKey.length);
if (!firebaseConfig.apiKey) {
    console.error("CRITICAL: VITE_FIREBASE_API_KEY is missing from the build!");
}

console.log("Firebase Init Attempt with keys starting with:", firebaseConfig.apiKey ? firebaseConfig.apiKey.substring(0, 5) : "MISSING");

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const storage = getStorage(app);
export const db = getFirestore(app);