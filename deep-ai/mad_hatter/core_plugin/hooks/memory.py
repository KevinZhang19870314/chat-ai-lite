from mad_hatter.decorators import hook
from langchain.docstore.document import Document

from memory.vector_memory import VectorMemoryCollection


# Hook called before a memory collection has been created.
# This happens at first launch and whenever the collection is deleted and recreated.
@hook(priority=0)
def before_collection_created(vector_memory_collection: VectorMemoryCollection, bot):
    """Do something before a new collection is created in vectorDB

    Parameters
    ----------
    vector_memory_collection : VectorMemoryCollection
        Instance of `VectorMemoryCollection` wrapping the actual db collection.
    bot : DeepAI
        DeepAI Bot instance.
    """
    pass


# Hook called after a memory collection has been created.
# This happens at first launch and whenever the collection is deleted and recreated.
@hook(priority=0)
def after_collection_created(vector_memory_collection: VectorMemoryCollection, bot):
    """Do something after a new collection is created in vectorDB

    Parameters
    ----------
    vector_memory_collection : VectorMemoryCollection
        Instance of `VectorMemoryCollection` wrapping the actual db collection.
    bot : DeepAI
        DeepAI Bot instance.
    """
    pass
