# Guía Git: ramas semanales

## Convención
- Rama de integración: `semana-10`, `semana-11`, ..., `semana-14`.
- Rol A: `s10-calidad-datos`, `s11-calidad-datos`, etc.
- Rol B: `s10-robustez`, `s11-robustez`, etc.
- Rol C: `s10-fuentes`, `s11-fuentes`, etc.

## Flujo
1. Actualizar `main`.
2. Crear rama semanal de integración desde `main`.
3. Crear las tres ramas individuales desde la rama semanal.
4. Cada integrante implementa solo los archivos de su rol.
5. Ejecutar pruebas individuales y realizar commits pequeños.
6. Abrir Pull Request hacia la rama semanal.
7. Integrar los tres Pull Requests y ejecutar pruebas de integración.
8. Abrir Pull Request de la rama semanal hacia `main`.
9. El docente o responsable de integración verifica criterios de aceptación.

## Reglas
- No trabajar directamente sobre `main`.
- No modificar archivos de otro rol sin coordinación.
- No cambiar contratos de `docs/contratos_modulos.md` unilateralmente.
- Resolver conflictos mediante comunicación y Pull Requests, no sobrescribiendo cambios.
- Cada integrante debe explicar su código individualmente.
