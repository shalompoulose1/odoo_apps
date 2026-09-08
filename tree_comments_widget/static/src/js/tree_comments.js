/** @odoo-module **/

import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

// ── Floating Comments Popup ───────────────────────────────────────────────────

class CommentsPanel extends Component {
    static template = "tree_comments_widget.CommentsPanel";
    static props = {
        resId: Number,
        resModel: String,
        displayName: { type: String, optional: true },
        anchorRef: Object,
        onClose: Function,
        onCommented: { type: Function, optional: true },
    };

    setup() {
        this.orm = useService("orm");
        this.popupRef = useRef("popup");
        this.textareaRef = useRef("textarea");
        this.state = useState({
            messages: [],
            loading: true,
            draft: "",
            posting: false,
            mentionQuery: null,
            mentionUsers: [],
            mentionIndex: 0,
        });
        this.popupStyle = "";
        this._outsideClick = this._onOutsideClick.bind(this);

        onMounted(async () => {
            this._positionPopup();
            await this.loadMessages();
            document.addEventListener("click", this._outsideClick, true);
        });
    }

    _positionPopup() {
        const anchor = this.props.anchorRef.el;
        if (!anchor) return;

        const rect = anchor.getBoundingClientRect();
        const POPUP_W = 340;
        const POPUP_H = 420;
        const GAP = 10;

        let left = rect.left - POPUP_W - GAP;
        if (left < 8) left = rect.right + GAP;

        let top = rect.top;
        const viewH = window.innerHeight;
        if (top + POPUP_H > viewH - 8) top = viewH - POPUP_H - 8;
        if (top < 8) top = 8;

        this.popupStyle = `position:fixed;left:${left}px;top:${top}px;width:${POPUP_W}px;z-index:1090`;
    }

    _onOutsideClick(ev) {
        const popup = this.popupRef.el;
        const anchor = this.props.anchorRef.el;
        if (!popup) return;
        if (!popup.contains(ev.target) && (!anchor || !anchor.contains(ev.target))) {
            document.removeEventListener("click", this._outsideClick, true);
            this.props.onClose();
        }
    }

    async loadMessages() {
        this.state.loading = true;
        try {
            const messages = await this.orm.searchRead(
                "mail.message",
                [
                    ["res_id", "=", this.props.resId],
                    ["model", "=", this.props.resModel],
                    ["message_type", "in", ["comment", "email"]],
                ],
                ["body", "author_id", "date"],
                { order: "date asc", limit: 200 }
            );
            this.state.messages = messages;
        } finally {
            this.state.loading = false;
        }
    }

    stripHtml(html) {
        if (!html) return "";
        const tmp = document.createElement("div");
        tmp.innerHTML = html;
        return tmp.textContent || tmp.innerText || "";
    }

    formatDate(dateStr) {
        if (!dateStr) return "";
        const d = new Date(dateStr.replace(" ", "T") + "Z");
        const now = new Date();
        const diff = now - d;
        if (diff < 60_000) return "Just now";
        if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
        if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
        return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
    }

    // ── @mention ─────────────────────────────────────────────────────────────

    get showMentions() {
        return this.state.mentionQuery !== null && this.state.mentionUsers.length > 0;
    }

    onInput(ev) {
        this._detectMention(ev.target);
    }

    _detectMention(textarea) {
        const pos = textarea.selectionStart;
        const textBefore = textarea.value.slice(0, pos);
        const lastAt = textBefore.lastIndexOf("@");

        if (lastAt === -1) { this._closeMention(); return; }

        const query = textBefore.slice(lastAt + 1);
        if (query.includes(" ")) { this._closeMention(); return; }

        this.state.mentionQuery = query;
        this._searchUsers(query);
    }

    async _searchUsers(query) {
        const domain = [["user_ids", "!=", false]];
        if (query) domain.push(["name", "ilike", query]);

        const users = await this.orm.searchRead(
            "res.partner",
            domain,
            ["id", "name"],
            { limit: 8, order: "name asc" }
        );

        if (this.state.mentionQuery === query) {
            this.state.mentionUsers = users;
            this.state.mentionIndex = 0;
        }
    }

    _closeMention() {
        this.state.mentionQuery = null;
        this.state.mentionUsers = [];
        this.state.mentionIndex = 0;
    }

    selectMention(user) {
        const textarea = this.textareaRef.el;
        if (!textarea) return;

        const pos = textarea.selectionStart;
        const text = this.state.draft;
        const textBefore = text.slice(0, pos);
        const lastAt = textBefore.lastIndexOf("@");
        if (lastAt === -1) return;

        const mention = `@${user.name} `;
        this.state.draft = text.slice(0, lastAt) + mention + text.slice(pos);
        this._closeMention();

        const newPos = lastAt + mention.length;
        setTimeout(() => {
            textarea.selectionStart = newPos;
            textarea.selectionEnd = newPos;
            textarea.focus();
        }, 0);
    }

    // ── Comment posting ──────────────────────────────────────────────────────

    async postComment() {
        const body = this.state.draft.trim();
        if (!body || this.state.posting) return;
        this.state.posting = true;
        try {
            await this.orm.call(
                this.props.resModel,
                "message_post",
                [[this.props.resId]],
                { body, message_type: "comment", subtype_xmlid: "mail.mt_comment" }
            );
            this.state.draft = "";
            await this.loadMessages();
            if (this.props.onCommented) this.props.onCommented();
        } finally {
            this.state.posting = false;
        }
    }

    onKeydown(ev) {
        if (this.state.mentionQuery !== null && this.state.mentionUsers.length) {
            if (ev.key === "ArrowDown") {
                ev.preventDefault();
                this.state.mentionIndex = (this.state.mentionIndex + 1) % this.state.mentionUsers.length;
                return;
            }
            if (ev.key === "ArrowUp") {
                ev.preventDefault();
                this.state.mentionIndex = (this.state.mentionIndex - 1 + this.state.mentionUsers.length) % this.state.mentionUsers.length;
                return;
            }
            if (ev.key === "Enter") {
                ev.preventDefault();
                this.selectMention(this.state.mentionUsers[this.state.mentionIndex]);
                return;
            }
            if (ev.key === "Escape") {
                ev.preventDefault();
                this._closeMention();
                return;
            }
        }
        if ((ev.ctrlKey || ev.metaKey) && ev.key === "Enter") {
            this.postComment();
        }
    }
}

// ── Button Field Widget ───────────────────────────────────────────────────────

class CommentsButtonWidget extends Component {
    static template = "tree_comments_widget.CommentsButtonWidget";
    static props = { ...standardFieldProps };
    static components = { CommentsPanel };

    setup() {
        this.state = useState({ open: false });
        this.wrapperRef = useRef("wrapper");
    }

    getModelName() {
        return this.props.record.resModel || "";
    }

    getDisplayName() {
        const data = this.props.record.data;
        const val = data.name || data.display_name || data.item_code;
        if (typeof val === 'string' && val) return val;
        if (Array.isArray(val) && val[1]) return String(val[1]);
        return String(this.props.record.resId || '');
    }

    togglePanel(ev) {
        ev.stopPropagation();
        this.state.open = !this.state.open;
    }

    closePanel() {
        this.state.open = false;
    }
}

registry.category("fields").add("comments_button", {
    component: CommentsButtonWidget,
    supportedTypes: ["integer"],
    extractProps: () => ({}),
});

