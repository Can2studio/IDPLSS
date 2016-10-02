import React, { Component, PropTypes } from 'react';
import { Router, Route, IndexRoute, Link } from 'react-router';
import { Row, Col, Button } from 'antd';
import classNames from 'classnames';

import styles from './TestCover.less';

const TestCover = ({ type }) => {
	const coverCls = () =>{
		/*if(type == 'small') return styles.small;
		if(type == 'big') return styles.big;*/
		return classNames({
			[styles[type]]:true,
		})
	};

	const renderTestCover = () =>{
		if (type == 'small') return <div className={styles.title}>试题题目</div>
			;
		if (type == 'big') return <Row>
			<Col lg={21} span={18}>
			<div className={styles.title}>试题题目</div>
			<div className={styles.subtitle}>出题人</div>
			</Col>
			<Col lg={3} span={6}>
			<Button className={styles.button}>开始测试</Button>
			</Col>
			</Row>
		;
	}
	return (
		<div className={coverCls()}>
			{renderTestCover()}
		</div>
	);
};

TestCover.propTypes = {  
	
};

export default TestCover;