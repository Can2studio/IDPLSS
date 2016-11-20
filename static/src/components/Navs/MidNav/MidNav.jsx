import React, { Component, PropTypes } from 'react';
import { Router, Route, IndexRoute, Link } from 'react-router';
import { Row, Col, Button } from 'antd';

import Search from '../Search/Search';
import NavCarousel from '../NavCarousel/NavCarousel';

import styles from './MidNav.less';

const MidNav = () => {
	return (
			<div>
				<div className={styles.nav}>
					<div className={styles.navcontain}>
						<Row className={styles.row}
								 align='middle'
						>
							<Col span={4}
							>
							<Button className={styles.active}><Link to={{ pathname:`/category/video/`}}>全部课程</Link></Button>
							</Col>
							<Col span={3}>
							<Button><Link to="/">首页</Link></Button>
							</Col>
							<Col span={3}>
							<Button><Link to={{ pathname:`/category/text/`}}>文库中心</Link></Button>
							</Col>
							<Col span={3}>
							<Button><Link to={{ pathname:`/category/test/`}}>在线测试</Link></Button>
							</Col>
							<Col span={3}>
							<Button><Link to={{ pathname:`/category/forum/`}}>学习交流</Link></Button>
							</Col>
							<Col span={6}
							>
							<Search />
							</Col>
						</Row>
						<div className={styles.position}>
							<div className={styles.navlist}>
								<Link to={{pathname:'/category/video/', hash: '#!/1/1'}}>
								<div className={styles.navcontext}>
								互联网/计算机
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/2/1'}}>
								<div className={styles.navcontext}>
								基础科学
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/3/1'}}>
								<div className={styles.navcontext}>
								工程技术
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/4/1'}}>
								<div className={styles.navcontext}>
								历史哲学
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/5/1'}}>
								<div className={styles.navcontext}>
								经管法律
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/6/1'}}>
								<div className={styles.navcontext}>
								语言文学
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/7/1'}}>
								<div className={styles.navcontext}>
								艺术音乐
								</div>
								</Link>
								<Link to={{pathname:'/category/video/', hash: '#!/8/1'}}>
								<div className={styles.navcontext}>
								兴趣生活
								</div>
								</Link>
							</div>
						</div>
					</div>
					
				</div>
				<NavCarousel />
			</div>
		);
}

MidNav.propTypes = {  
	//text: PropTypes.element.isRequired,
	/*text: PropTypes.oneOfType([
	      React.PropTypes.string,
	      React.PropTypes.number,
  ]),*/
};

export default MidNav;