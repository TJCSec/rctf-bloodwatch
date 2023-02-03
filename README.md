# rctf-bloodwatch
[rctf-bloodwatch from redpwn](https://github.com/redpwn/rctf-bloodwatch) but in Python. The only additional feature is selecting specific divisions to count (to exclude admins, for example).

## Usage

| argument                   | environment       | required | default         | type                                                      | description                 |
| -------------------------- | ----------------- | -------- | --------------- | --------------------------------------------------------- | --------------------------- |
| `-u` / `--url`             | `RCTF_URL`        | yes      | _(none)_        | string                                                    | rCTF URL to monitor         |
| `-t` / `--token`           | `RCTF_TOKEN`      | yes      | _(none)_        | string                                                    | rCTF API token              |
| `-d` / `--division`        | `RCTF_DIVISION`   | no       | _all divisions_ | string                                                    | rCTF division(s) to include |
| `-w` / `--discord-webhook` | `DISCORD_WEBHOOK` | yes      | _(none)_        | string                                                    | Discord webhook URL         |
| `-m` / `--message`         | `BLOOD_MESSAGE`   | yes      | _(none)_        | string                                                    | Message to send to webhook  |
| `-i` / `--interval`        | `BLOOD_INTERVAL`  | no       | 60              | integer                                                   | Seconds between checks      |
| `-l` / `--log-level`       | `LOG_LEVEL`       | no       | `INFO`          | `NOTSET \| DEBUG \| INFO \| WARNING \| ERROR \| CRITICAL` | Log level                   |

### Divisions
`--division` can be specified multiple times to include multiple divisions. Alternatively, specify a space-separated list in `RCTF_DIVISION`.

### Message
`--message` is a template string with these variables available:

- `challenge` (challenge object)
- `blooder` (solve object)

See [rCTF](https://github.com/redpwn/rctf) for the shape of these objects. Here's an example message:

```
Congratulations to [`{{ blooder.userName | replace("`", "") }}`](<https://ctf.tjcsec.club/profile/{{ blooder.userId }}>) for first blood on `{{ challenge.name }}`!
```

This sends a message that looks like this:

![example webhook message](./images/example.png)

## Sample Usage
```yaml
version: '3'
services:
  blood:
    image: ghcr.io/tjcsec/rctf-bloodwatch
    restart: always
    environment:
      - RCTF_TOKEN=sice
      - DISCORD_WEBHOOK=deets
    command: ['-u', 'http://rctf/', '-m', 'Congratulations to [`{{ blooder.userName | replace("`", "") }}`](<https://rctf/profile/{{ blooder.userId }}>) for first blood on `{{ challenge.category }}/{{ challenge.name }}`!']
```
