# Rationale

Small utility script for renaming files to match series information found on thetvdb.com. Useful for when your files have episode names in them, but not the season or episode information necessary for scaping in Kodi.

---

# Installation

1. Clone / copy this repo
1. `pip install -r requirements.txt`
1. Move `ttvdb-renamer.py` into your `PATH`

Requires an API key located in ~/.config/ttvdb/api_key, which you can get for
free [here](https://thetvdb.com/api-information).

# Usage

The script is self-documenting, but basic usage would be:

```sh
thetvdb-renamer.py 'Disney Animated Shorts'
```

This will work automatically for files named

```sh
[series-name-or-anything].[episode-name].extension
```

resulting in them being renamed:

```sh
[series-name-or-anything].S[season-number]E[episode-number].extension
```

If the delimiter is not '.', you can specify it with `-d`. If the position of the episode name is not after the first delimiter, you can specify how many delimiters precede it with `-n`. So for example, given the name:

```sh
[series-name]-[something-else]-[episode-name].extension
```

you would pass these options:

```sh
thetvdb-renamer.py 'Disney Animated Shorts' -d '-' -n 2
```

You can also use the `-b` flag to avoid asking for confirmation on each rename.

Please be warned that _this script renames files_, and I have only done very limited manual testing for my own use case.
