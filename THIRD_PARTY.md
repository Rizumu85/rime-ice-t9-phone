# Third-Party Scheme References

The numeric Stroke scheme adapts the code map and generates
`t9_stroke.dict.yaml` from a pinned revision of
[Rime Stroke](https://github.com/rime/rime-stroke), licensed under LGPL-3.0.
The generated table keeps complete Han ideographs, removes unrelated Unicode
stroke/component data, and gives supplementary-plane Han a low mobile priority
because glyph support varies by Android device and font. The pinned source
revision and reproducible transformation are recorded in
`scripts/generate_t9_stroke_dictionary.py`.

The Zhuyin phonetic conversion rules are adapted from
[Rime Bopomofo](https://github.com/rime/rime-bopomofo), licensed under
LGPL-3.0. The phone-key grouping was cross-checked against the experimental
[TT9 Bopomofo/Zhuyin fork](https://github.com/taitungsun/tt9-bopomofo-zhuyin),
but no TT9 source code or dictionary data is copied into this repository.

`predict.db` is the `data-1.0` prediction database published by
[librime-predict](https://github.com/rime/librime-predict). It was built from
Rime Essay and Octagram data and is redistributed under the librime-predict
BSD-3-Clause license. The unmodified upstream binary is used so prediction
quality and database compatibility remain owned by the Rime project.
