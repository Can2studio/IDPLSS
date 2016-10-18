import React, { PropTypes } from 'react';
import { Router, Route, IndexRoute, Link, Redirect } from 'react-router';
import { connect } from 'react-redux';
import pathToRegexp from 'path-to-regexp';
import cookie from 'js-cookie';

import App from '../components/App';
import Index from '../pages/Index'
import Category from '../pages/Category';
import Detail from '../pages/Detail';
import PostDetail from '../pages/PostDetail';
import Register from '../pages/Register';
import User from '../pages/User';
import PlayVideo from '../pages/PlayVideo';
// import PlayText from '../pages/PlayText';
import PlayTest from '../pages/PlayTest';
import NotFound from '../pages/NotFound';

//import { initPageStore } from './initPageStore';

const Routes = ({ history, dispatch }) =>{
	//initPageStore(history,dispatch);
	history.listen(({ pathname, hash }) =>{
		
		// 注册初始化------------------
		if(pathname.search('register')!== -1){
			const match = pathToRegexp('#!/:token').exec(hash);
			if(match){
				dispatch({
					type: 'user/register/confirm',
					confirm_code: match[1]
				})
			}
		}
		//分类页初始化-------------------
		if(pathname.search('category')!== -1){
			const matchpathname = pathToRegexp('/category/:context/').exec(pathname)
			const context = matchpathname[1];
			dispatch({
				type: `${context}/init/categorySource`
			})

			if(hash){
				const match = pathToRegexp('#!/:category/:pagination').exec(hash);
				const category = parseInt(match[1]);
				const pagination = parseInt(match[2]);
				dispatch({
					type: `${context}/init/commplete/categorySource`,
					category: category,
					pagination: pagination,
				})
			}
			else{
				dispatch({
					type: `${context}/init/commplete/categorySource`,
					category: 0,
					pagination: 1,
				})
			}
			dispatch({
				type: `${context}/get/categorySource`
			})
		}
		//end------------------------
		// detail init-------------------
		if(pathname.search('detail')!== -1 || pathname.search('post')!== -1){
			let match, context, id, fuc;
			// comment detail
			if(pathname.search('detail')!== -1){
				match = pathToRegexp('/detail/:context/:id/#!/:fuc/:pagination/').exec(pathname+hash);
				context = match[1]
				id = match[2]
				fuc = match[3]
				dispatch({
					type: `${context}/get/detail`,
					id: id
				})
				dispatch({
					type: `${context}/get/${fuc}`,
					id: id,
					pagination: match[4]
				})
			}
			// post detail
			if(pathname.search('post')!== -1){
				match = pathToRegexp('/post/:id/#!/:pagination/').exec(pathname+hash);
				context = 'forum'
				id = match[1]
				dispatch({
					type: `${context}/get/detail`,
					id: id
				})
				dispatch({
					type: 'forum/get/comment',
					id: id,
					pagination: match[2]
				})
			}
			
			// dispatch({
			// 	type: `${context}/init/detail`,
			// 	id: id,
			// })
			// if(hash){
			// 	// 除了论坛都有hash
			// 	const matchHash = pathToRegexp('#!/:fuc/:pagination').exec(hash)
			// 	const fuc = matchHash[1]
			// 	// dispatch({
			// 	// 	type: `${context}/init/detail`,
			// 	// 	id: id,
			// 	// 	fuc: fuc,
			// 	// })
			// 	dispatch({
			// 		type: `${context}/get/${fuc}`,
			// 		id: id,
			// 		pagination: matchHash[2]
			// 	})
			// }else{
			// 	dispatch({
			// 		type: 'forum/get/comment',
			// 		id: id,
			// 		pagination: match[2]
			// 	})
			// }
		}
		// -------------end--------------------
		// -test problem init------------------
		if(pathname.search('play/test')!== -1){
			const match = pathToRegexp('/play/test/:testId/:recordId').exec(pathname);
			dispatch({
				type: 'test/init/problem',
				testId: match[1],
				testRecordId: match[2],
			})
			dispatch({
				type: 'test/get/series'
			})
		}

		// login listen----------------------
		if(cookie.get('user_id') && cookie.get('authorization')){

			dispatch({
				type: 'user/get/loginInfo',
				user_id: cookie.get('user_id')
			})
		}
		// user zone init-----------------------
		if(pathname.search('user')!== -1){
			
			const match = pathToRegexp('/user/:id/').exec(pathname)
			dispatch({
				type: 'user/get/info',
				user_id: match[1]
			})
		}
	})
	return(
	<Router history={history}>
		<Route path="/index" component={Index}>
			<Redirect from="/" to="/index" />
		</Route>
		<Route path="/category/" component={Category}>
			<Route path="video/" >
			</Route>
			<Route path="text/"  />
			<Route path="test/"  />
			<Route path="forum/" />
		</Route>
		<Route path="/detail/" component={Detail}>
			<Route path="video/:id/" />
			<Route path="text/:id/" />
			<Route path="test/:id/" />
			<Route path="*" component={NotFound}  />
		</Route>
		<Route path="/post/:id/" component={PostDetail} />
		<Route path="/user/:id/" component={User}>
		</Route>
		<Route path="/register/" component={Register}>
		</Route>
		<Route path="/play/" >
			<Route path="video/:id/" component={PlayVideo}  />
			{/*<Route path="text/:id/" component={PlayText}  />*/}
			<Route path="test/:testId/:recordId/" component={PlayTest}  />
			<Route path="*" component={NotFound}  />
		</Route>
		{/*<Route path="/actived" component={App} />*/}
		{/*<Route path="/completed" component={App} />*/}
		<Route path="/demo" component={App}/>
		<Route path="*" component={NotFound}/>

	</Router>
	)

}

Routes.propTypes = {
	history: PropTypes.any,
};

function mapStoretoPorp(){
	return({})
}

export default connect(mapStoretoPorp)(Routes);
