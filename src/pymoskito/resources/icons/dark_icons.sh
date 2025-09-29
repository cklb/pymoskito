#! /usr/bin/sh

# generate dark versions of the icons
for icon in light/icons/*.png; do
  magick $icon -alpha extract -background "#e0e0e0" -alpha shape ${icon/light/dark}
#  magick $icon -channel RGB -negate ${icon/light/dark}
done