# Feature Specification: elo-rating-service

**Feature Branch**: `001-elo-rating-service`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Se creará un servicio para implementar el algorimo de ELO (para consultar aclaraciones se tomará como referencia la documentación de https://en.wikipedia.org/wiki/Elo_rating_system). La API estará implementada con FastAPI usando pyhton 3.11+. La persistencia se realizará con MongoDB. La aplicación también consumirá y publicará eventos en Kafka. La API definirá por un lado un CRUD de jugadores. Los jugadores (player) tendrán un id autogenerado en formato UUID, un id_external, name, elo y otra información necesaria. También tendrá un CRUD de ligas de jugadores (league) que tendrán una parametrización preconfigurada de k_factor que podrá ser modificado durante la creación. La API también expondrá un método en el que se registrará el resultado de una partida entre dos jugadores. Este método recibirá los identificadores de los jugadores (idFirst, idSecond) y un idWiner que indicará el ganador o será nulo cuando el resultado sea un empate. La API estará documentada con OpenApi (code-first). Las variables de configuración se establecerán como variables de sistema a partir de un fichero .env. Se crearan test unitarios de los componentes para ser testeados mockeando la capa de infraestructura. Se usarán los patrones de port-adapters de arquitectura hexagonal. La API definirá un objeto de error generico para los errores 4xx. Los métodos de consulta de la API estarán implementados usando búsquedas RSQL usando el parametro q para la expresion RSQL, page y size para la paginación. La API debe exponer un endpoint /health de salud. El endpoint de salud no debe realizar comprobaciones profundas que afecten al rendimiento."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage players (Priority: P1)

Como operador de la plataforma quiero crear, leer, actualizar y eliminar jugadores para mantener el catálogo de participantes.

**Why this priority**: Sin gestión de jugadores no se puede calcular ni registrar partidas.

**Independent Test**: Llamar al CRUD de `player` (create/read/update/delete) y verificar persistencia en MongoDB (mock en tests unitarios).

**Acceptance Scenarios**:

1. **Given** un payload válido, **When** se invoca `POST /players`, **Then** se crea un jugador con `id` UUID y `elo` inicial por defecto.
2. **Given** un `id` existente, **When** se invoca `GET /players/{id}`, **Then** se devuelve el jugador.
3. **Given** datos modificados, **When** se invoca `PUT /players/{id}`, **Then** se actualiza el jugador.
4. **Given** un `id` existente, **When** se invoca `DELETE /players/{id}`, **Then** el jugador se marca/elimna y no aparece en listados.

---

### User Story 2 - Manage leagues (Priority: P1)

Como operador quiero crear y gestionar ligas con su `k_factor` para controlar la sensibilidad del rating.

**Why this priority**: Los cálculos ELO dependen de parámetros de liga.

**Independent Test**: Llamar al CRUD de `league` y verificar `k_factor` aplicable a partidas asociadas.

**Acceptance Scenarios**:

1. **Given** un payload válido, **When** se invoca `POST /leagues`, **Then** se crea la liga con `k_factor` provisto o con el valor por defecto.
2. **Given** `league_id`, **When** se invoca `GET /leagues/{id}`, **Then** devuelve la configuración de la liga.

---

### User Story 3 - Registrar resultado de partida (Priority: P1)

Como sistema quiero registrar el resultado de una partida entre dos jugadores para recalcular sus ratings y publicar/consumir eventos relevantes.

**Why this priority**: Es la acción que modifica ratings; motor del valor del servicio.

**Independent Test**: Llamar al endpoint `POST /matches` (o similar) con `idFirst`, `idSecond`, `idWinner` (o null para empate) y verificar que:

- Se calcula y persiste el nuevo `elo` para ambos jugadores (tests unitarios con capa de infraestructura mockeada).
- Se persiste un registro de la partida con timestamp y metadatos mínimos.
- Se publica un evento a Kafka con el resultado y las diferencias de rating.

**Acceptance Scenarios**:

1. **Given** dos jugadores válidos y `idWinner` igual al `idFirst`, **When** se registra la partida, **Then** se actualizan ambos ratings según algoritmo ELO y se publica evento `match.result`.
2. **Given** empate (`idWinner` nulo), **When** se registra la partida, **Then** se calculan ratings de empate y se publica evento con resultado `draw`.

---

### Edge Cases

- Registro de partida cuando uno o ambos jugadores no existen → devolver error 4xx (objeto de error genérico).
- Registro duplicado de la misma partida (idempotencia) → detectar por `external_match_id` si se proporciona.
- Cambios de `k_factor` en una liga con partidas previas → aplicar el nuevo `k_factor` solo a partir de su creación (no recomputar histórico por defecto) [ASSUMPTION].

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: API MUST exponer CRUD REST para `players` con `id` UUID autogenerado, `id_external`, `name`, `elo` (float), y campos adicionales opcionales.
- **FR-002**: API MUST exponer CRUD REST para `leagues` con `id` UUID autogenerado, `name` y `k_factor` configurable en creación y actualización.
- **FR-003**: API MUST exponer un endpoint para registrar resultados de partidas: recibe `idFirst`, `idSecond`, `idWinner` (UUID | null), `league_id` (UUID) y `external_match_id` (opcional). Las partidas se registran y calculan siempre en el contexto de una liga.
- **FR-004**: Al registrar una partida, el sistema MUST calcular los nuevos ratings ELO para los jugadores afectados siguiendo la especificación de Wikipedia como referencia y persistir los cambios.
- **FR-005**: Al registrar una partida, el sistema MUST persistir un registro de la partida con `timestamp`, `players`, `result`, `elo_before` y `elo_after` para cada jugador.
- **FR-006**: El sistema MUST publicar un evento en Kafka (`match.result`) con la información relevante tras procesar la partida, y aceptar consumir eventos de Kafka si la aplicación debe recibir resultados externos.
- **FR-007**: Todas las consultas lista/busqueda MUST soportar RSQL vía parámetro `q` y paginación con `page` y `size`.
- **FR-008**: La API MUST documentarse con OpenAPI (code-first) y proveer esquema de request/response y errores.
- **FR-009**: Configuración MUST leerse desde variables de entorno cargadas por un fichero `.env` (ej. mediante `python-dotenv` o equivalente en runtime).
- **FR-010**: La arquitectura del servicio MUST seguir patrón hexagonal (port-adapters); la capa de dominio y casos de uso será testeable y desacoplada de MongoDB/Kafka.
- **FR-011**: Se MUST proporcionar tests unitarios para componentes de dominio y casos de uso; las pruebas de infraestructura (Mongo/Kafka) serán mockeadas en unit tests.
- **FR-012**: La API MUST definir un objeto de error genérico para respuestas 4xx con estructura estandarizada `{code, message, details?}`.
- **FR-013**: La API MUST exponer un endpoint `/health` que realice una comprobación ligera (no chequeos profundos que afecten rendimiento).

- **FR-014**: Players MUST pertenecer a una `league` (cada `player` tiene una referencia obligatoria a `league_id`). Todas las partidas se calculan en el contexto de la liga asociada.
- **FR-015**: Si `k_factor` no es provisto al crear una liga, usar un valor por defecto de `32`.

### Key Entities *(include if feature involves data)*

- **Player**: `id` (UUID), `id_external` (string|null), `name` (string), `elo` (float), `created_at`, `updated_at`, `metadata` (map).
- **League**: `id` (UUID), `name`, `k_factor` (float), `created_at`, `updated_at`, `metadata`.
- **Match / Game**: `id` (UUID), `external_match_id` (optional), `league_id` (optional), `player_a_id`, `player_b_id`, `winner_id` (nullable), `score` (optional), `timestamp`, `elo_before` (map), `elo_after` (map).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: CRUD básico (players, leagues) implementado y cubierto por tests unitarios con >90% de casos críticos simulados.
- **SC-002**: Registro de partidas con recalculo de ratings produce resultados determinísticos acorde a la fórmula ELO de referencia en >99% de casos de prueba unitarios.
- **SC-003**: Endpoints de consulta responden con paginación y filtros RSQL; 95% de queries simples responden en <500ms en condiciones razonables (documentar entorno de referencia).
- **SC-004**: Documentación OpenAPI generada y accesible vía la ruta por defecto de FastAPI.

## Assumptions

- Los cálculos ELO seguirán la referencia pública de Wikipedia salvo casos especiales documentados.
- `k_factor` es un parámetro por liga y se aplica a partidas a partir del momento en que la liga existe; por defecto NO se recomputará histórico cuando cambie `k_factor`.
Se asumirá `players` deben estar asociados a una `league` (campo `league_id` obligatorio en `player`).
`k_factor` por defecto será `32` si no se proporciona al crear la liga.
- Persistencia primaria será MongoDB y las colecciones deberán modelarse para lectura eficiente de historial de partidas.
- Kafka será accesible en entorno de despliegue; en pruebas unitarias las interacciones con Kafka serán mockeadas.
