import * as dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'
import utc from "dayjs/plugin/utc"

function setupDayjs() {
	dayjs.locale('zh-cn')
	dayjs.extend(utc);
}

export default setupDayjs
