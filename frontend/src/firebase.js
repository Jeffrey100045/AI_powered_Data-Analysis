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

console.log("Firebase Diagnostic Check:", {
    hasApiKey: !!firebaseConfig.apiKey,
    hasAuthDomain: !!firebaseConfig.authDomain,
    hasProjectId: !!firebaseConfig.projectId,
    apiKeyLength: firebaseConfig.apiKey.length
});

if (!firebaseConfig.apiKey) {
    throw new Error("CRITICAL: VITE_FIREBASE_API_KEY is missing from the build. Check Render Environment Variables.");
}

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const storage = getStorage(app);
export const db = getFirestore(app);