// Navegación dura a la landing (recarga completa): descarta todo el estado
// en memoria del panel. Para cerrar sesión y para el borrado de cuenta.
export function goToLanding(): void {
  window.location.assign("/");
}
