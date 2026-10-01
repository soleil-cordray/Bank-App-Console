// src/auth/roles.js
// The same role groups the backend uses (app/dependencies.py + controllers).
// The frontend uses them to decide which links and pages to SHOW;
// the backend still does the real checking (401 / 403) on every request.

// POST /transactions/transfer
export const CAN_TRANSFER = ['CUSTOMER', 'ADMIN']

// GET /branches/analytics/*
export const MANAGERS = ['BRANCH_MANAGER', 'ADMIN']
