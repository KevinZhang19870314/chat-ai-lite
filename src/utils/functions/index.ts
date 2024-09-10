import dayjs from "dayjs"

export function getCurrentDate() {
	const date = new Date()
	const day = date.getDate()
	const month = date.getMonth() + 1
	const year = date.getFullYear()
	return `${year}-${month}-${day}`
}

export function formatDateToYYYYMMDDHHMMSS(dateString: string) {
	const date = new Date(dateString)

	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0') // Months are zero-based
	const day = String(date.getDate()).padStart(2, '0')
	const hours = String(date.getHours()).padStart(2, '0')
	const minutes = String(date.getMinutes()).padStart(2, '0')
	const seconds = String(date.getSeconds()).padStart(2, '0')

	return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

export function formatDateStringToLocal(dateString: string) {
	if (!dateString.endsWith('Z')) {
		dateString += 'Z';
	}

	const date = dayjs(dateString).utc().local();
	const localDateString = date.format('MM/DD/YYYY h:mm A');

	return localDateString;
}

export function generateSessionId() {
	const timestamp = Date.now().toString() // Get current timestamp
	const randomNum = Math.floor(Math.random() * 10000).toString() // Generate a random number

	const sessionId = timestamp + randomNum // Concatenate timestamp and random number
	return +sessionId
}

export function arrayBufferToJson(arrayBuffer: ArrayBuffer) {
	const decoder = new TextDecoder('utf-8')
	const decodedString = decoder.decode(arrayBuffer)
	const json = JSON.parse(decodedString)
	return json
}

export function downloadBlob(blob: any, filenameWithExt: string) {
	// 创建一个URL对象，并用它来创建一个a标签的href属性
	const url = window.URL.createObjectURL(new Blob([blob]))
	const link = document.createElement('a')
	link.href = url
	link.setAttribute('download', filenameWithExt)
	document.body.appendChild(link)
	link.click()

	// 清理并释放URL对象
	link.parentNode?.removeChild(link)
	window.URL.revokeObjectURL(url)
}
