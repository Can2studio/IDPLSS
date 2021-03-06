import xFetch from './xFetch';

let apiUrl = 'http://api.jxnugo.com'
// let apiUrl = '127.0.0.1:5000'
export let data = {}

export async function getTestCategory(action) {
	let url;
	if (data['category']!== -1 ) url = apiUrl+'/api/test-list/category/'+data['category']+'?page='+data['pagination']
	else url = apiUrl+'/api/test-list?page='+data['pagination']
  	return xFetch(url,{method: 'GET',});
}
export async function getTestRecommend(action) {
	return xFetch(`${apiUrl}/api/recommend/popular-tests`,{method: 'GET',});
}
export async function getTestDetail(action) {
	return xFetch(`${apiUrl}/api/test-list/detail/${action.id}`,{method: 'GET',});
}

export async function getTestDetailList(action) {
	let url = `${apiUrl}/api/`;
	if(action.count == 'part') url += `test-list/${action.id}/problems?page=${action.pagination}`;
	if(action.count == 'all') url += `user/${action.id}/self-test-problems`;
	
	return xFetch(url,{method: 'GET',});
}

// export async function postTestDetailComment(action) {
// 	return xFetch(apiUrl+'/api/courses/detail/'+data['coursesId']+'/new-comment',{method: 'POST',
// 		body: JSON.stringify(data['body']),
// 	});
// }

// export async function deleteTestDetailComment(action) {
// 	return xFetch(apiUrl+'/api/courses/detail/comment/'+data['commentId'],{method: 'DELETE',});
// }
export async function TestAnswer(action) {
	if(action.type == 'test/post/problemResult'){
		console.log(1)
		return xFetch(`${apiUrl}/api/test-list/test-answer/${action.id}`,{method: 'POST',
			body: JSON.stringify(action.body),
		});
	}
	if(action.type == 'test/get/problemResult'){
		console.log(2)
		return xFetch(`${apiUrl}/api/test-list/over-test/${action.id}`,{method: 'GET',});
	}
	
}