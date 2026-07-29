from unittest.mock import patch

from scripts import parser


class TestParser:
    def test_parses_gems_from_page(self, sample_gems_html):
        with (
            patch.object(parser, "_fetch_gems_html", return_value=sample_gems_html),
            patch.object(parser, "_write_gems_json") as write,
        ):
            parser.main()

        (written,) = write.call_args.args
        assert [gem.name for gem in written] == [
            "Barrage",
            "Boneshatter",
            "Lightning Arrow",
            "Spark",
        ]
        assert [gem.weapons for gem in written] == [
            ["Bow", "Spear"],
            [],
            ["Bow"],
            ["Occult"],
        ]

    def test_gem_id_matches_known_value(self):
        # Pinned so swapping the hash or digest size cannot silently remap every
        # id and orphan the points already stored in Qdrant.
        assert parser._gem_id("Lightning_Arrow") == 98517804654556

    def test_gem_id_differs_per_slug(self):
        slugs = ["Lightning_Arrow", "Boneshatter", "Barrage", "Spark"]
        ids = {parser._gem_id(slug) for slug in slugs}
        assert len(ids) == len(slugs)

    def test_gem_id_fits_unsigned_48_bits(self):
        for slug in ["Lightning_Arrow", "Boneshatter", "Barrage", "Spark"]:
            gem_id = parser._gem_id(slug)
            assert 0 < gem_id < 2**48

    def test_description_spacing(self, sample_gems_html):
        # Inline keyword links are flattened into the sentence. Node boundaries
        # must neither gain a space ("non- Herald", "Armour .") nor lose one
        # ("ChainingLightning").
        gems = {gem.name: gem for gem in parser._parse_gems_html(sample_gems_html)}

        assert gems["Lightning Arrow"].description == (
            "Fire a charged arrow that releases Chaining Lightning beams at non-Herald enemies."
        )
        assert gems["Boneshatter"].description == (
            "Strike with a forceful blow, weakening their Armour."
        )
