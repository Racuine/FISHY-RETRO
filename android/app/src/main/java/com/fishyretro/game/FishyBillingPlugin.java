package com.fishyretro.game;

import androidx.annotation.NonNull;

import com.android.billingclient.api.*;
import com.getcapacitor.*;
import com.getcapacitor.annotation.CapacitorPlugin;

import java.util.*;

@CapacitorPlugin(name = "FishyBilling")
public class FishyBillingPlugin extends Plugin implements PurchasesUpdatedListener {

    private BillingClient client;
    private PluginCall activeCall;

    private final Set<String> allowed = new HashSet<>(Arrays.asList(
        "fishy_bronze",
        "fishy_silver",
        "fishy_gold",
        "fishy_platinum",
        "fishy_emerald",
        "fishy_ruby",
        "fishy_sapphire",
        "fishy_amethyst",
        "fishy_diamond",
        "fishy_black_diamond"
    ));

    @Override
    public void load() {
        client = BillingClient.newBuilder(getContext())
            .setListener(this)
            .enablePendingPurchases(
                PendingPurchasesParams.newBuilder()
                    .enableOneTimeProducts()
                    .build()
            )
            .build();
    }

    private void connect(Runnable ok, PluginCall call) {

        if (client.isReady()) {
            ok.run();
            return;
        }

        client.startConnection(new BillingClientStateListener() {

            @Override
            public void onBillingSetupFinished(@NonNull BillingResult result) {

                if (result.getResponseCode() == BillingClient.BillingResponseCode.OK) {
                    ok.run();
                } else {
                    call.reject(
                        "Google Play indisponible : " + result.getDebugMessage()
                    );
                }
            }

            @Override
            public void onBillingServiceDisconnected() {
                // Une nouvelle connexion sera tentée au prochain appel.
            }
        });
    }

    @PluginMethod
    public void purchase(PluginCall call) {

        String id = call.getString("productId", "");

        if (!allowed.contains(id)) {
            call.reject("Produit inconnu");
            return;
        }

        if (activeCall != null) {
            call.reject("Un achat est déjà en cours");
            return;
        }

        connect(() -> {

            QueryProductDetailsParams params =
                QueryProductDetailsParams.newBuilder()
                    .setProductList(
                        Collections.singletonList(
                            QueryProductDetailsParams.Product.newBuilder()
                                .setProductId(id)
                                .setProductType(BillingClient.ProductType.INAPP)
                                .build()
                        )
                    )
                    .build();

            client.queryProductDetailsAsync(params, (result, details) -> {

                // Vérification de la réponse Google Play Billing.
                if (result.getResponseCode() != BillingClient.BillingResponseCode.OK) {
                    call.reject(
                        "Erreur Google Play Billing : " + result.getDebugMessage()
                    );
                    return;
                }

                // Google Play Billing 8 retourne un QueryProductDetailsResult.
                List<ProductDetails> products = details.getProductDetailsList();

                if (products == null || products.isEmpty()) {
                    call.reject("Produit Google Play introuvable ou non publié");
                    return;
                }

                ProductDetails detail = products.get(0);

                BillingFlowParams flow =
                    BillingFlowParams.newBuilder()
                        .setProductDetailsParamsList(
                            Collections.singletonList(
                                BillingFlowParams.ProductDetailsParams.newBuilder()
                                    .setProductDetails(detail)
                                    .build()
                            )
                        )
                        .build();

                activeCall = call;

                BillingResult launch =
                    client.launchBillingFlow(getActivity(), flow);

                if (launch.getResponseCode() != BillingClient.BillingResponseCode.OK) {

                    activeCall = null;

                    call.reject(
                        "Impossible d'ouvrir Google Play : " +
                        launch.getDebugMessage()
                    );
                }
            });

        }, call);
    }

    @Override
    public void onPurchasesUpdated(
        @NonNull BillingResult result,
        List<Purchase> purchases
    ) {

        PluginCall call = activeCall;
        activeCall = null;

        if (call == null) {
            return;
        }

        if (result.getResponseCode() == BillingClient.BillingResponseCode.USER_CANCELED) {
            call.reject("Achat annulé");
            return;
        }

        if (
            result.getResponseCode() != BillingClient.BillingResponseCode.OK ||
            purchases == null ||
            purchases.isEmpty()
        ) {
            call.reject(
                "Paiement échoué : " + result.getDebugMessage()
            );
            return;
        }

        Purchase purchase = purchases.get(0);

        if (purchase.getProducts() == null || purchase.getProducts().isEmpty()) {
            call.reject("Aucun produit associé à cet achat");
            return;
        }

        JSObject data = new JSObject();

        data.put("productId", purchase.getProducts().get(0));
        data.put("purchaseToken", purchase.getPurchaseToken());

        data.put(
            "pending",
            purchase.getPurchaseState() != Purchase.PurchaseState.PURCHASED
        );

        call.resolve(data);
    }

    @PluginMethod
    public void restorePurchases(PluginCall call) {

        connect(() -> {

            QueryPurchasesParams params =
                QueryPurchasesParams.newBuilder()
                    .setProductType(BillingClient.ProductType.INAPP)
                    .build();

            client.queryPurchasesAsync(params, (result, purchases) -> {

                if (result.getResponseCode() != BillingClient.BillingResponseCode.OK) {

                    call.reject(
                        "Restauration impossible : " + result.getDebugMessage()
                    );

                    return;
                }

                JSArray list = new JSArray();

                for (Purchase purchase : purchases) {

                    if (
                        purchase.getPurchaseState() !=
                        Purchase.PurchaseState.PURCHASED
                    ) {
                        continue;
                    }

                    for (String id : purchase.getProducts()) {

                        JSObject obj = new JSObject();

                        obj.put("productId", id);
                        obj.put(
                            "purchaseToken",
                            purchase.getPurchaseToken()
                        );

                        list.put(obj);
                    }
                }

                JSObject data = new JSObject();

                data.put("purchases", list);

                call.resolve(data);
            });

        }, call);
    }

    @Override
    protected void handleOnDestroy() {

        if (client != null) {
            client.endConnection();
        }

        super.handleOnDestroy();
    }
}
