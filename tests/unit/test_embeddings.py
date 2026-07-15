from app.rag.embeddings import get_embeddings, embedding_model


class TestEmbeddings:
    async def test_returns_correct_shape_and_type(self):
        expected_dim = embedding_model.get_embedding_dimension()
        data_to_embed = [
            "test1",
            "test2",
            "test3",
        ]

        embeddings = await get_embeddings(data_to_embed)
        assert len(embeddings) == len(data_to_embed)
        assert all(len(vec) == expected_dim for vec in embeddings)
        assert all(isinstance(x, float) for vec in embeddings for x in vec)

    async def test_empty_input(self):
        data_to_embed = []
        embeddings = await get_embeddings(data_to_embed)
        assert len(embeddings) == 0
