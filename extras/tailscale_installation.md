# Instal·lació de Tailscale

**Autors:** Eric Lopez, Nil Parra

La documentació completa de la instal·lació i configuració de Tailscale es troba a [`tailscale_doc.md`](tailscale_doc.md).

## Per què Tailscale

L'arquitectura de replicació de la base de dades requereix connexió entre el servidor cloud i la xarxa privada local. La infraestructura està sota NAT de l'ISP i protegida per un firewall, cosa que impedeix una connexió directa.

S'han avaluat diverses opcions:

| Opció | Decisió | Motiu |
|---|---|---|
| Ngrok (túnel TCP) | Descartat | Requereix pagament i té limitacions |
| Túnel SSH | Descartat | Inestable per a connexions persistents |
| Tailscale (VPN) | **Escollit** | Estable, open source, gratuït i fàcil de gestionar |

## Fitxers

- `tailscale_doc.md` — documentació detallada de la instal·lació pas a pas al servidor local i al servidor cloud.
- `images/` — captures de pantalla del procés d'instal·lació.
