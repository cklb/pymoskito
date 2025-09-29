#! /usr/bin/sh

for icon in icons/light/icons/*.png; do
  magick $icon -channel RGB -negate ${icon/light/dark}
done