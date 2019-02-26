package com.example.android.uqmapp;

import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import com.google.firebase.database.DataSnapshot;
import com.google.firebase.database.DatabaseError;
import com.google.firebase.database.DatabaseReference;
import com.google.firebase.database.FirebaseDatabase;
import com.google.firebase.database.ValueEventListener;

import java.util.Objects;


public class MainActivity extends AppCompatActivity {
    TextView temp, humidity, air, light, pressure;
    final DatabaseReference reference = FirebaseDatabase.getInstance().getReference().child("urban-quality-monitor");

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        temp = (TextView) findViewById(R.id.temp);
        humidity = findViewById(R.id.humid);
        air = findViewById(R.id.air);
        light = findViewById(R.id.light);
        pressure = findViewById(R.id.pressure);

    }

    @Override
    protected void onStart()
    {
        super.onStart();
        reference.addValueEventListener(new ValueEventListener() {
            @Override
            public void onDataChange(DataSnapshot dataSnapshot) {
                temp.setText(dataSnapshot.child("Temperature").getValue(Float.class).toString());
                 humidity.setText(dataSnapshot.child("Humidity").getValue(Float.class).toString());
                air.setText(dataSnapshot.child("Air Quality").getValue().toString());
                light.setText(dataSnapshot.child("Ambient Light").getValue().toString());
                pressure.setText(dataSnapshot.child("Pressure").getValue(Integer.class).toString());
            }

            @Override
            public void onCancelled(@NonNull DatabaseError databaseError) {

            }

        });
    }
}