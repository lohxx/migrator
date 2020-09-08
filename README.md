
## Installation

clone this repository and run the pip command.

```bash
pip install .
```

## Config

Add the following environment variables, with the ids and secrets supplied by the streaming service.
DEEZER_CLIENT_ID, DEEZER_CLIENT_SECRET
SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

Spotify - https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app
Deezer - https://developers.deezer.com/guidelines/getting_started

## Usage

```bash
copy-playlist --from-service=spotify --to-service=deezer --playlist-name=xyz
```
![usage](https://github.com/lohxx/migrator/blob/master/versao_final.gif)


## Supported services
- Spotify
- Deezer
- ~~Youtube~~
