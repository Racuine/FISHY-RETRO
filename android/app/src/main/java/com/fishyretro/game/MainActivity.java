package com.fishyretro.game;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;
public class MainActivity extends BridgeActivity {
 @Override public void onCreate(Bundle savedInstanceState) {
  registerPlugin(FishyBillingPlugin.class);
  super.onCreate(savedInstanceState);
 }
}
