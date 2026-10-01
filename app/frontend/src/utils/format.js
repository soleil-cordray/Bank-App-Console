// src/utils/format.js
// Small helpers for showing money and dates the same way on every page.

const dollars = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' })

// 1234.5 -> "$1,234.50"
export function formatMoney(amount) {
  return dollars.format(amount)
}

// "2026-09-30T14:05:00" -> "Sep 30, 2026, 10:05 AM" (in the viewer's time zone)
// The backend saves UTC times but sends them WITHOUT a time zone, which
// JavaScript would read as local time. Adding "Z" marks them as UTC.
export function formatDate(value) {
  const hasZone = /Z|[+-]\d\d:\d\d$/.test(value)
  return new Date(hasZone ? value : `${value}Z`).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}
