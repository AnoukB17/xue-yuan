#!/bin/sh
# Reconstruit vendor/firebase-10.14.1.js : SDK Firebase (app, auth, firestore) en un seul module ES.
# Usage : sh tools/build-firebase.sh   (demande npm et un accès au registre npm)
set -e
OUT="$(cd "$(dirname "$0")/.." && pwd)/vendor/firebase-10.14.1.js"
T=$(mktemp -d); cd "$T"
npm init -y >/dev/null && npm i firebase@10.14.1 esbuild@0.24.0 >/dev/null
cat > entry.js <<'JS'
export * as app from 'firebase/app';
import {getAuth, onAuthStateChanged, createUserWithEmailAndPassword, sendEmailVerification, signInWithEmailAndPassword, reload, signOut, sendPasswordResetEmail, deleteUser, applyActionCode, verifyPasswordResetCode, confirmPasswordReset} from 'firebase/auth';
import {getFirestore, doc, getDoc, setDoc, deleteDoc, onSnapshot, collection, getDocs} from 'firebase/firestore';
export const auth = {getAuth, onAuthStateChanged, createUserWithEmailAndPassword, sendEmailVerification, signInWithEmailAndPassword, reload, signOut, sendPasswordResetEmail, deleteUser, applyActionCode, verifyPasswordResetCode, confirmPasswordReset};
export const firestore = {getFirestore, doc, getDoc, setDoc, deleteDoc, onSnapshot, collection, getDocs};
JS
npx esbuild entry.js --bundle --format=esm --minify --target=es2020 --legal-comments=eof --outfile="$OUT"
rm -rf "$T"; echo "OK : $OUT"
