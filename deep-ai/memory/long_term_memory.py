from memory.vector_memory import VectorMemory


# This class represents the Bot long term memory (content the bot saves on disk).
class LongTermMemory:
    def __init__(self, vector_memory_config={}):
        # Vector based memory (will store embeddings and their metadata)
        self.vectors = VectorMemory(**vector_memory_config)

        # What type of memory is coming next?
        # Surprise surprise, my dear!
