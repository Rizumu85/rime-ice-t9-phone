# Third-Party Scheme References

The numeric Stroke scheme adapts the code map and generates
`t9_stroke.dict.yaml` from a pinned revision of
[Rime Stroke](https://github.com/rime/rime-stroke), licensed under LGPL-3.0.
The generated table keeps complete Han ideographs and removes unrelated
Unicode stroke/component data. The pinned source revision and reproducible
transformation are recorded in `scripts/generate_t9_stroke_dictionary.py`.

The Zhuyin phonetic conversion rules are adapted from
[Rime Bopomofo](https://github.com/rime/rime-bopomofo), licensed under
LGPL-3.0. The phone-key grouping was cross-checked against the experimental
[TT9 Bopomofo/Zhuyin fork](https://github.com/taitungsun/tt9-bopomofo-zhuyin),
but no TT9 source code or dictionary data is copied into this repository.
