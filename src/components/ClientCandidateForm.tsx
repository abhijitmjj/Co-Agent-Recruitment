"use client";

import dynamic from 'next/dynamic';

// Dynamically load the client-side CandidateForm, disabling SSR
export default dynamic(
  () => import('./candidate-form'),
  { ssr: false }
);