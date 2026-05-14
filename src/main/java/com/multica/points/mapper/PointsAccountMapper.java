package com.multica.points.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.multica.points.entity.PointsAccount;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

import java.math.BigDecimal;

@Mapper
public interface PointsAccountMapper extends BaseMapper<PointsAccount> {

    @Update("UPDATE points_account SET balance = balance + #{amount}, total_earned = total_earned + #{amount}, version = version + 1 WHERE user_id = #{userId} AND version = #{version}")
    int addBalance(@Param("userId") String userId, @Param("amount") BigDecimal amount, @Param("version") Integer version);

    @Update("UPDATE points_account SET balance = balance - #{amount}, total_spent = total_spent + #{amount}, version = version + 1 WHERE user_id = #{userId} AND balance >= #{amount} AND version = #{version}")
    int deductBalance(@Param("userId") String userId, @Param("amount") BigDecimal amount, @Param("version") Integer version);

    @Select("SELECT * FROM points_account WHERE user_id = #{userId}")
    PointsAccount selectByUserId(@Param("userId") String userId);
}
