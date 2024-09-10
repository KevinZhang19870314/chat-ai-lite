import localForage from 'localforage'

interface StorageData<T = any> {
  data: T
}

export function createIndexedDB() {
  async function set<T = any>(key: string, data: T) {
    const storageData: StorageData<T> = {
      data,
    }

    const json = JSON.stringify(storageData)
    await localForage.setItem(key, json)
  }

  async function get(key: string) {
    const json = await localForage.getItem<any>(key)
    if (json) {
      let storageData: StorageData | null = null

      try {
        storageData = JSON.parse(json)
      }
      catch {
        // Prevent failure
      }

      if (storageData) {
        const { data } = storageData
        return data
      }

      return null
    }
  }

  async function remove(key: string) {
    await localForage.removeItem(key)
  }

  async function clear() {
    await localForage.clear()
  }

  return {
    set,
    get,
    remove,
    clear,
  }
}

export const indexedDB = createIndexedDB()
