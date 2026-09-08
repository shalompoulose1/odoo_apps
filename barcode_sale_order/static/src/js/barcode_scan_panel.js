import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useBus, useService } from "@web/core/utils/hooks";
import { BarcodeScanner } from "@barcodes/components/barcode_scanner";
import { Component, useState } from "@odoo/owl";

/**
 * Barcode scanning panel embedded on the Sale Order form view.
 *
 * Reuses the core `barcode` service (USB/keyboard-wedge scanner detection,
 * see addons/barcodes/static/src/barcode_service.js) for hardware scanners,
 * and the core `barcodes.BarcodeScanner` component (camera scanning) for
 * mobile/camera input, instead of reimplementing either.
 */
export class BarcodeScanPanel extends Component {
    static template = "barcode_sale_order.ScanPanel";
    static components = { BarcodeScanner };
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.barcodeService = useService("barcode");
        this.state = useState({
            active: false,
            lastBarcode: "",
            productName: "",
            qty: null,
            busy: false,
            manualBarcode: "",
        });
        this.scanQueue = [];
        useBus(this.barcodeService.bus, "barcode_scanned", (ev) => this.onBarcodeScanned(ev.detail.barcode));
    }

    get record() {
        return this.props.record;
    }

    toggleActive() {
        if (!this.record.resId) {
            this.notification.add(_t("Please save the order before scanning."), { type: "warning" });
            return;
        }
        this.state.active = !this.state.active;
    }

    onBarcodeScanned(barcode) {
        if (!this.state.active) {
            return;
        }
        // Queue scans instead of dropping them: a fast scanner can fire many
        // 'barcode_scanned' events before the previous RPC has resolved.
        this.scanQueue.push(barcode);
        this.processQueue();
    }

    onManualSubmit(ev) {
        ev.preventDefault();
        this.submitManualBarcode();
    }

    submitManualBarcode() {
        const barcode = this.state.manualBarcode.trim();
        this.state.manualBarcode = "";
        if (!barcode || !this.state.active) {
            return;
        }
        this.scanQueue.push(barcode);
        this.processQueue();
    }

    async processQueue() {
        if (this.state.busy) {
            return;
        }
        this.state.busy = true;
        try {
            while (this.scanQueue.length) {
                const barcode = this.scanQueue.shift();
                await this.processBarcode(barcode);
            }
        } finally {
            this.state.busy = false;
        }
    }

    async processBarcode(barcode) {
        this.state.lastBarcode = barcode;
        try {
            if (await this.record.isDirty()) {
                await this.record.save();
            }
            const result = await this.orm.call(
                "sale.order",
                "action_scan_barcode",
                [[this.record.resId], barcode]
            );
            if (result.status === "ok") {
                this.state.productName = result.product_name;
                this.state.qty = result.qty;
                await this.record.load();
            } else {
                this.notification.add(result.message, {
                    type: result.status === "not_found" ? "warning" : "danger",
                });
            }
        } catch {
            this.notification.add(_t("Could not reach the server. Please check your connection and try again."), {
                type: "danger",
            });
        }
    }
}

export const barcodeScanPanel = {
    component: BarcodeScanPanel,
};

registry.category("view_widgets").add("barcode_scan_panel", barcodeScanPanel);
