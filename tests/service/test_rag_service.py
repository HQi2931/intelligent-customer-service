"""RagSummarizeService 服务测试。"""



class TestRagSummarizeServiceInit:
    def test_init_chain_exists(self, mocker):
        mocker.patch("rag.rag_service.VectorStoreService")
        mocker.patch("rag.rag_service.load_rag_prompts", return_value="测试模板")
        mocker.patch("rag.rag_service.chat_model")

        from rag.rag_service import RagSummarizeService
        service = RagSummarizeService()
        assert service.chain is not None

    def test_init_chain_method_name(self):
        """验证方法名已从 __init___chain 修正为 _init_chain。"""
        from rag.rag_service import RagSummarizeService
        assert hasattr(RagSummarizeService, "_init_chain")
        assert not hasattr(RagSummarizeService, "__init___chain")


class TestRagSummarizeServiceInvoke:
    def test_rag_summarize_calls_chain(self, mocker):
        mocker.patch("rag.rag_service.VectorStoreService")
        mocker.patch("rag.rag_service.load_rag_prompts", return_value="{input}\n{context}")
        mocker.patch("rag.rag_service.chat_model")

        mock_chain = mocker.MagicMock()
        mock_chain.invoke.return_value = "测试回答"
        mocker.patch.object(
            __import__("rag.rag_service", fromlist=["RagSummarizeService"]).RagSummarizeService,
            "_init_chain",
            return_value=mock_chain,
        )

        import rag.rag_service as rsvc
        from rag.rag_service import RagSummarizeService
        # 重新创建实例，让 mock 生效
        rsvc.VectorStoreService = mocker.MagicMock()
        rsvc.load_rag_prompts = mocker.MagicMock(return_value="{input}\n{context}")
        rsvc.chat_model = mocker.MagicMock()

        service = RagSummarizeService.__new__(RagSummarizeService)
        service.prompt_template = mocker.MagicMock()
        service.chain = mock_chain
        service.retriever = mocker.MagicMock()
        service.retriever.invoke.return_value = []

        result = service.rag_summarize("测试查询")
        assert result == "测试回答"
        mock_chain.invoke.assert_called_once()
