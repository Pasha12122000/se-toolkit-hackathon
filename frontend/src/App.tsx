import { FormEvent, useEffect, useState } from "react";

type Locale = "ru" | "en";
type Role = "owner" | "worker";

type Section = {
  id: string;
  label: string;
  category_count: number;
  item_count: number;
};

type Category = {
  key: string;
  label: string;
  section_id: string;
  item_count: number;
};

type MenuItem = {
  id: string;
  name: string;
  description: string;
  price_rub: number;
  category_label: string;
  section_label: string;
  is_popular: boolean;
};

type HighlightItem = {
  id: string;
  name: string;
  category_label: string;
  price_rub: number;
};

type AgentRecommendation = {
  id: string;
  name: string;
  category_label: string;
  price_rub: number;
  reason: string;
};

type AgentResponse = {
  answer: string;
  recommendations: AgentRecommendation[];
};

type AdminProfile = {
  username: string;
  full_name: string;
  title: string;
  role: Role;
};

type StaffMember = {
  id: number;
  username: string;
  full_name: string;
  title_ru: string;
  title_en: string;
  role: Role;
};

type StaffSummary = {
  total_admins: number;
  owner_count: number;
  worker_count: number;
  members: StaffMember[];
};

type MenuItemForm = {
  id: string;
  name_ru: string;
  name_en: string;
  category: string;
  category_ru: string;
  category_en: string;
  section_id: "food" | "drinks" | "sushi";
  section_ru: string;
  section_en: string;
  price_rub: string;
  description_ru: string;
  description_en: string;
  is_popular: boolean;
  keywords: string;
};

type WorkerForm = {
  username: string;
  password: string;
  full_name: string;
  title_ru: string;
  title_en: string;
};

const texts = {
  ru: {
    badge: "Халяль меню рядом, без очереди",
    heroTitle: "Happiness Menu",
    heroText:
      "Быстрый доступ к меню Happiness Cafe для студентов, сотрудников и гостей кампуса. Сначала выбираешь раздел, потом категорию, и сразу видишь актуальные позиции.",
    highlights: "Популярное сейчас",
    sections: "Меню по блокам",
    categories: "Категории",
    items: "Позиции",
    searchPlaceholder: "Поиск по меню: латте, салат, шаурма",
    emptySearch: "Начни вводить запрос, и мы покажем подходящие позиции.",
    admin: "Админ-панель",
    adminWelcome: "Войти как сотрудник кафе",
    login: "Войти",
    logout: "Выйти",
    username: "Логин",
    password: "Пароль",
    adminHint: "Демо-доступ: owner / owner123",
    owner: "Владелец",
    worker: "Работник",
    staff: "Команда кафе",
    totalAdmins: "Всего админов",
    owners: "Владельцы",
    workers: "Работники",
    saveItem: "Сохранить позицию",
    deleteItem: "Удалить позицию",
    editItem: "Редактировать",
    addWorker: "Добавить работника",
    removeWorker: "Удалить",
    itemEditor: "Редактор меню",
    workerEditor: "Управление сотрудниками",
    menuId: "ID позиции",
    nameRu: "Название RU",
    nameEn: "Название EN",
    categoryRaw: "Категория ключ",
    categoryRu: "Категория RU",
    categoryEn: "Category EN",
    section: "Раздел",
    sectionRu: "Раздел RU",
    sectionEn: "Section EN",
    price: "Цена, RUB",
    descriptionRu: "Описание RU",
    descriptionEn: "Описание EN",
    keywords: "Ключевые слова через запятую",
    popular: "Популярная позиция",
    fullName: "Имя и фамилия",
    titleRu: "Должность RU",
    titleEn: "Job title EN",
    searchTitle: "Быстрый поиск",
    agentTitle: "Menu Assistant Agent",
    agentText: "Спроси агента, что заказать. Он смотрит актуальное меню и подбирает варианты по бюджету и предпочтениям.",
    agentPlaceholder: "Например: что взять до 300 рублей из напитков?",
    askAgent: "Спросить агента",
    ready: "Готово",
  },
  en: {
    badge: "Halal cafe menu without waiting in line",
    heroTitle: "Happiness Menu",
    heroText:
      "A bilingual web menu for Happiness Cafe. Pick a section, open a category, and instantly see the latest items before you walk to the counter.",
    highlights: "Popular right now",
    sections: "Browse by section",
    categories: "Categories",
    items: "Items",
    searchPlaceholder: "Search the menu: latte, salad, shawarma",
    emptySearch: "Start typing and the menu search will suggest matching items.",
    admin: "Admin Panel",
    adminWelcome: "Sign in as cafe staff",
    login: "Sign in",
    logout: "Sign out",
    username: "Username",
    password: "Password",
    adminHint: "Demo access: owner / owner123",
    owner: "Owner",
    worker: "Worker",
    staff: "Cafe team",
    totalAdmins: "Total admins",
    owners: "Owners",
    workers: "Workers",
    saveItem: "Save item",
    deleteItem: "Delete item",
    editItem: "Edit",
    addWorker: "Add worker",
    removeWorker: "Remove",
    itemEditor: "Menu editor",
    workerEditor: "Staff management",
    menuId: "Item ID",
    nameRu: "Name RU",
    nameEn: "Name EN",
    categoryRaw: "Category key",
    categoryRu: "Category RU",
    categoryEn: "Category EN",
    section: "Section",
    sectionRu: "Section RU",
    sectionEn: "Section EN",
    price: "Price, RUB",
    descriptionRu: "Description RU",
    descriptionEn: "Description EN",
    keywords: "Keywords separated by commas",
    popular: "Popular item",
    fullName: "Full name",
    titleRu: "Title RU",
    titleEn: "Title EN",
    searchTitle: "Quick search",
    agentTitle: "Menu Assistant Agent",
    agentText: "Ask the agent what to order. It checks the live menu and recommends options by budget and preferences.",
    agentPlaceholder: "Example: what drink can I get under 300 RUB?",
    askAgent: "Ask agent",
    ready: "Done",
  },
} as const;

const defaultSections: MenuItemForm["section_id"][] = ["food", "drinks", "sushi"];

const defaultItemForm: MenuItemForm = {
  id: "",
  name_ru: "",
  name_en: "",
  category: "",
  category_ru: "",
  category_en: "",
  section_id: "food",
  section_ru: "Еда",
  section_en: "Food",
  price_rub: "",
  description_ru: "",
  description_en: "",
  is_popular: false,
  keywords: "",
};

const defaultWorkerForm: WorkerForm = {
  username: "",
  password: "",
  full_name: "",
  title_ru: "",
  title_en: "",
};

function App() {
  const [locale, setLocale] = useState<Locale>("ru");
  const [sections, setSections] = useState<Section[]>([]);
  const [selectedSection, setSelectedSection] = useState<string>("food");
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [items, setItems] = useState<MenuItem[]>([]);
  const [highlights, setHighlights] = useState<HighlightItem[]>([]);
  const [search, setSearch] = useState("");
  const [searchResults, setSearchResults] = useState<MenuItem[]>([]);
  const [agentQuestion, setAgentQuestion] = useState("");
  const [agentResponse, setAgentResponse] = useState<AgentResponse | null>(null);
  const [agentLoading, setAgentLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [adminOpen, setAdminOpen] = useState(false);
  const [adminToken, setAdminToken] = useState(() => localStorage.getItem("happiness_admin_token") ?? "");
  const [profile, setProfile] = useState<AdminProfile | null>(null);
  const [staffSummary, setStaffSummary] = useState<StaffSummary | null>(null);
  const [loginForm, setLoginForm] = useState({ username: "", password: "" });
  const [itemForm, setItemForm] = useState<MenuItemForm>(defaultItemForm);
  const [workerForm, setWorkerForm] = useState<WorkerForm>(defaultWorkerForm);
  const [feedback, setFeedback] = useState("");

  const t = texts[locale];

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`/api/menu/sections?locale=${locale}`).then((res) => res.json()),
      fetch(`/api/menu/highlights?locale=${locale}`).then((res) => res.json()),
    ])
      .then(([sectionData, highlightData]: [Section[], HighlightItem[]]) => {
        setSections(sectionData);
        setHighlights(highlightData);
        if (!sectionData.some((section) => section.id === selectedSection)) {
          setSelectedSection(sectionData[0]?.id ?? "food");
        }
      })
      .finally(() => setLoading(false));
  }, [locale, selectedSection]);

  useEffect(() => {
    fetch(`/api/menu/sections/${selectedSection}/categories?locale=${locale}`)
      .then((res) => res.json())
      .then((data: Category[]) => {
        setCategories(data);
        setSelectedCategory((current) =>
          data.some((category) => category.key === current) ? current : (data[0]?.key ?? ""),
        );
      });
  }, [selectedSection, locale]);

  useEffect(() => {
    if (!selectedCategory) {
      setItems([]);
      return;
    }

    fetch(`/api/menu/categories/${encodeURIComponent(selectedCategory)}/items?locale=${locale}`)
      .then((res) => res.json())
      .then((data: MenuItem[]) => setItems(data));
  }, [selectedCategory, locale]);

  useEffect(() => {
    if (!search.trim()) {
      setSearchResults([]);
      return;
    }

    const timeout = setTimeout(() => {
      fetch(`/api/menu/search?q=${encodeURIComponent(search)}&locale=${locale}`)
        .then((res) => res.json())
        .then((data: MenuItem[]) => setSearchResults(data));
    }, 200);

    return () => clearTimeout(timeout);
  }, [search, locale]);

  useEffect(() => {
    if (!adminToken) {
      setProfile(null);
      setStaffSummary(null);
      return;
    }

    Promise.all([
      fetch("/api/admin/me", { headers: { Authorization: `Bearer ${adminToken}` } }).then((res) => res.json()),
      fetch("/api/admin/staff", { headers: { Authorization: `Bearer ${adminToken}` } }).then((res) => res.json()),
    ]).then(([profileData, staffData]) => {
      setProfile(profileData);
      setStaffSummary(staffData);
    });
  }, [adminToken]);

  function handleLogin(event: FormEvent) {
    event.preventDefault();
    fetch("/api/admin/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(loginForm),
    })
      .then(async (res) => {
        if (!res.ok) throw new Error("Login failed");
        return res.json();
      })
      .then((data: { token: string; profile: AdminProfile }) => {
        localStorage.setItem("happiness_admin_token", data.token);
        setAdminToken(data.token);
        setProfile(data.profile);
        setFeedback(t.ready);
      })
      .catch(() => setFeedback("Login failed"));
  }

  function handleLogout() {
    localStorage.removeItem("happiness_admin_token");
    setAdminToken("");
    setProfile(null);
    setFeedback("");
  }

  function syncItemFormFromCurrentCategory() {
    const currentSection = sections.find((section) => section.id === selectedSection);
    const currentCategory = categories.find((category) => category.key === selectedCategory);
    setItemForm((current) => ({
      ...current,
      category: currentCategory?.key ?? current.category,
      category_ru: locale === "ru" ? currentCategory?.label ?? current.category_ru : current.category_ru,
      category_en: locale === "en" ? currentCategory?.label ?? current.category_en : current.category_en,
      section_id: (currentSection?.id as MenuItemForm["section_id"]) ?? current.section_id,
      section_ru: currentSection?.id === "drinks" ? "Напитки" : currentSection?.id === "sushi" ? "Суши и роллы" : "Еда",
      section_en: currentSection?.id === "drinks" ? "Drinks" : currentSection?.id === "sushi" ? "Sushi and Rolls" : "Food",
    }));
  }

  function handleSaveItem(event: FormEvent) {
    event.preventDefault();
    fetch("/api/admin/items", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${adminToken}`,
      },
      body: JSON.stringify({
        ...itemForm,
        price_rub: Number(itemForm.price_rub),
        keywords: itemForm.keywords
          .split(",")
          .map((part) => part.trim())
          .filter(Boolean),
      }),
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Save failed");
        return payload;
      })
      .then((payload: { message: string }) => {
        setFeedback(payload.message);
        setItemForm(defaultItemForm);
        if (selectedCategory) {
          return fetch(`/api/menu/categories/${encodeURIComponent(selectedCategory)}/items?locale=${locale}`)
            .then((res) => res.json())
            .then((data: MenuItem[]) => setItems(data));
        }
      })
      .catch((error: Error) => setFeedback(error.message));
  }

  function handleDeleteItem(itemId: string) {
    fetch(`/api/admin/items/${itemId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${adminToken}` },
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Delete failed");
        return payload;
      })
      .then((payload: { message: string }) => {
        setFeedback(payload.message);
        setItems((current) => current.filter((item) => item.id !== itemId));
      })
      .catch((error: Error) => setFeedback(error.message));
  }

  function handleEditItem(itemId: string) {
    fetch(`/api/admin/items/${itemId}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Load failed");
        return payload as MenuItemForm & { keywords: string[] };
      })
      .then((payload) =>
        setItemForm({
          ...payload,
          price_rub: String(payload.price_rub),
          keywords: payload.keywords.join(", "),
        }),
      )
      .catch((error: Error) => setFeedback(error.message));
  }

  function handleAddWorker(event: FormEvent) {
    event.preventDefault();
    fetch("/api/admin/staff", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${adminToken}`,
      },
      body: JSON.stringify(workerForm),
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Create failed");
        return payload;
      })
      .then((payload: { message: string }) => {
        setFeedback(payload.message);
        setWorkerForm(defaultWorkerForm);
        return fetch("/api/admin/staff", {
          headers: { Authorization: `Bearer ${adminToken}` },
        })
          .then((res) => res.json())
          .then((data: StaffSummary) => setStaffSummary(data));
      })
      .catch((error: Error) => setFeedback(error.message));
  }

  function handleRemoveWorker(workerId: number) {
    fetch(`/api/admin/staff/${workerId}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${adminToken}` },
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Remove failed");
        return payload;
      })
      .then((payload: { message: string }) => {
        setFeedback(payload.message);
        return fetch("/api/admin/staff", {
          headers: { Authorization: `Bearer ${adminToken}` },
        })
          .then((res) => res.json())
          .then((data: StaffSummary) => setStaffSummary(data));
      })
      .catch((error: Error) => setFeedback(error.message));
  }

  function handleAskAgent(event: FormEvent) {
    event.preventDefault();
    const question = agentQuestion.trim();
    if (!question) return;

    setAgentLoading(true);
    fetch("/api/agent/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, locale }),
    })
      .then(async (res) => {
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.detail ?? "Agent failed");
        return payload as AgentResponse;
      })
      .then((payload) => setAgentResponse(payload))
      .catch((error: Error) =>
        setAgentResponse({
          answer: error.message,
          recommendations: [],
        }),
      )
      .finally(() => setAgentLoading(false));
  }

  return (
    <div className="page-shell">
      <div className="background-glow background-glow-left" />
      <div className="background-glow background-glow-right" />

      <header className="topbar">
        <div>
          <p className="brand-kicker">{t.badge}</p>
          <h1 className="brand-name">{t.heroTitle}</h1>
        </div>

        <div className="topbar-actions">
          <button className="ghost-button" onClick={() => setLocale(locale === "ru" ? "en" : "ru")}>
            {locale === "ru" ? "English Version" : "Русская версия"}
          </button>
          <button className="primary-button" onClick={() => setAdminOpen((current) => !current)}>
            {t.admin}
          </button>
        </div>
      </header>

      <main className="layout">
        <section className="hero-card">
          <p>{t.heroText}</p>
          <div className="highlight-grid">
            {highlights.map((item) => (
              <article key={item.id} className="highlight-card">
                <span>{item.category_label}</span>
                <strong>{item.name}</strong>
                <small>{item.price_rub} RUB</small>
              </article>
            ))}
          </div>
        </section>

        <section className="menu-grid">
          <article className="panel">
            <h2>{t.sections}</h2>
            <div className="section-grid">
              {loading ? <p>Loading...</p> : null}
              {sections.map((section) => (
                <button
                  key={section.id}
                  className={section.id === selectedSection ? "section-card section-card-active" : "section-card"}
                  onClick={() => setSelectedSection(section.id)}
                >
                  <strong>{section.label}</strong>
                  <span>
                    {section.category_count} / {section.item_count}
                  </span>
                </button>
              ))}
            </div>
          </article>

          <article className="panel">
            <h2>{t.categories}</h2>
            <div className="chip-wrap">
              {categories.map((category) => (
                <button
                  key={category.key}
                  className={category.key === selectedCategory ? "chip chip-active" : "chip"}
                  onClick={() => setSelectedCategory(category.key)}
                >
                  {category.label} <span>{category.item_count}</span>
                </button>
              ))}
            </div>
          </article>
        </section>

        <section className="content-grid">
          <article className="panel">
            <div className="panel-header">
              <h2>{t.items}</h2>
              {adminToken ? (
                <button className="ghost-button small-button" onClick={syncItemFormFromCurrentCategory}>
                  {locale === "ru" ? "Заполнить из текущей категории" : "Use current category"}
                </button>
              ) : null}
            </div>

            <div className="item-grid">
              {items.map((item) => (
                <article key={item.id} className="item-card">
                  <div className="item-header">
                    <span className="item-category">{item.category_label}</span>
                    {item.is_popular ? <span className="item-badge">Hot</span> : null}
                  </div>
                  <h3>{item.name}</h3>
                  <p>{item.description}</p>
                  <div className="item-footer">
                    <strong>{item.price_rub} RUB</strong>
                    {adminToken ? (
                      <div className="admin-item-actions">
                        <button className="link-button" onClick={() => handleEditItem(item.id)}>
                          {t.editItem}
                        </button>
                        <button className="link-button" onClick={() => handleDeleteItem(item.id)}>
                          {t.deleteItem}
                        </button>
                      </div>
                    ) : null}
                  </div>
                </article>
              ))}
            </div>
          </article>

          <article className="panel">
            <h2>{t.searchTitle}</h2>
            <input
              className="search-input"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder={t.searchPlaceholder}
            />
            {searchResults.length === 0 ? (
              <p className="muted-text">{t.emptySearch}</p>
            ) : (
              <div className="search-results">
                {searchResults.map((item) => (
                  <article key={item.id} className="search-card">
                    <strong>{item.name}</strong>
                    <span>{item.category_label}</span>
                    <small>{item.price_rub} RUB</small>
                  </article>
                ))}
              </div>
            )}
          </article>

          <article className="panel agent-panel">
            <h2>{t.agentTitle}</h2>
            <p className="muted-text">{t.agentText}</p>
            <form className="agent-form" onSubmit={handleAskAgent}>
              <input
                className="search-input"
                value={agentQuestion}
                onChange={(event) => setAgentQuestion(event.target.value)}
                placeholder={t.agentPlaceholder}
              />
              <button className="primary-button" type="submit" disabled={agentLoading}>
                {agentLoading ? "..." : t.askAgent}
              </button>
            </form>
            {agentResponse ? (
              <div className="agent-answer">
                <p>{agentResponse.answer}</p>
                <div className="search-results">
                  {agentResponse.recommendations.map((item) => (
                    <article key={item.id} className="search-card">
                      <strong>{item.name}</strong>
                      <span>{item.category_label}</span>
                      <small>
                        {item.price_rub} RUB • {item.reason}
                      </small>
                    </article>
                  ))}
                </div>
              </div>
            ) : null}
          </article>
        </section>
      </main>

      {adminOpen ? (
        <aside className="admin-drawer">
          <div className="admin-header">
            <div>
              <p className="drawer-kicker">{t.admin}</p>
              <h2>{profile ? profile.full_name : t.adminWelcome}</h2>
            </div>
            {profile ? (
              <button className="ghost-button small-button" onClick={handleLogout}>
                {t.logout}
              </button>
            ) : null}
          </div>

          {!profile ? (
            <form className="admin-form" onSubmit={handleLogin}>
              <label>
                {t.username}
                <input
                  value={loginForm.username}
                  onChange={(event) => setLoginForm((current) => ({ ...current, username: event.target.value }))}
                />
              </label>
              <label>
                {t.password}
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(event) => setLoginForm((current) => ({ ...current, password: event.target.value }))}
                />
              </label>
              <button className="primary-button" type="submit">
                {t.login}
              </button>
              <p className="muted-text">{t.adminHint}</p>
            </form>
          ) : (
            <div className="admin-content">
              <div className="stats-grid">
                <article className="stat-card">
                  <span>{t.totalAdmins}</span>
                  <strong>{staffSummary?.total_admins ?? 0}</strong>
                </article>
                <article className="stat-card">
                  <span>{t.owners}</span>
                  <strong>{staffSummary?.owner_count ?? 0}</strong>
                </article>
                <article className="stat-card">
                  <span>{t.workers}</span>
                  <strong>{staffSummary?.worker_count ?? 0}</strong>
                </article>
              </div>

              <section>
                <h3>{t.staff}</h3>
                <div className="staff-list">
                  {staffSummary?.members.map((member) => (
                    <article key={member.id} className="staff-card">
                      <div>
                        <strong>{member.full_name}</strong>
                        <p>{locale === "ru" ? member.title_ru : member.title_en}</p>
                        <small>{member.role === "owner" ? t.owner : t.worker}</small>
                      </div>
                      {profile.role === "owner" && member.role === "worker" ? (
                        <button className="link-button" onClick={() => handleRemoveWorker(member.id)}>
                          {t.removeWorker}
                        </button>
                      ) : null}
                    </article>
                  ))}
                </div>
              </section>

              <section>
                <h3>{t.itemEditor}</h3>
                <form className="admin-form" onSubmit={handleSaveItem}>
                  <label>
                    {t.menuId}
                    <input value={itemForm.id} onChange={(event) => setItemForm((current) => ({ ...current, id: event.target.value }))} />
                  </label>
                  <label>
                    {t.nameRu}
                    <input value={itemForm.name_ru} onChange={(event) => setItemForm((current) => ({ ...current, name_ru: event.target.value }))} />
                  </label>
                  <label>
                    {t.nameEn}
                    <input value={itemForm.name_en} onChange={(event) => setItemForm((current) => ({ ...current, name_en: event.target.value }))} />
                  </label>
                  <label>
                    {t.categoryRaw}
                    <input value={itemForm.category} onChange={(event) => setItemForm((current) => ({ ...current, category: event.target.value }))} />
                  </label>
                  <label>
                    {t.categoryRu}
                    <input value={itemForm.category_ru} onChange={(event) => setItemForm((current) => ({ ...current, category_ru: event.target.value }))} />
                  </label>
                  <label>
                    {t.categoryEn}
                    <input value={itemForm.category_en} onChange={(event) => setItemForm((current) => ({ ...current, category_en: event.target.value }))} />
                  </label>
                  <label>
                    {t.section}
                    <select
                      value={itemForm.section_id}
                      onChange={(event) =>
                        setItemForm((current) => ({
                          ...current,
                          section_id: event.target.value as MenuItemForm["section_id"],
                        }))
                      }
                    >
                      {defaultSections.map((sectionId) => (
                        <option key={sectionId} value={sectionId}>
                          {sectionId}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label>
                    {t.sectionRu}
                    <input value={itemForm.section_ru} onChange={(event) => setItemForm((current) => ({ ...current, section_ru: event.target.value }))} />
                  </label>
                  <label>
                    {t.sectionEn}
                    <input value={itemForm.section_en} onChange={(event) => setItemForm((current) => ({ ...current, section_en: event.target.value }))} />
                  </label>
                  <label>
                    {t.price}
                    <input value={itemForm.price_rub} onChange={(event) => setItemForm((current) => ({ ...current, price_rub: event.target.value }))} />
                  </label>
                  <label>
                    {t.descriptionRu}
                    <textarea value={itemForm.description_ru} onChange={(event) => setItemForm((current) => ({ ...current, description_ru: event.target.value }))} />
                  </label>
                  <label>
                    {t.descriptionEn}
                    <textarea value={itemForm.description_en} onChange={(event) => setItemForm((current) => ({ ...current, description_en: event.target.value }))} />
                  </label>
                  <label>
                    {t.keywords}
                    <input value={itemForm.keywords} onChange={(event) => setItemForm((current) => ({ ...current, keywords: event.target.value }))} />
                  </label>
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={itemForm.is_popular}
                      onChange={(event) => setItemForm((current) => ({ ...current, is_popular: event.target.checked }))}
                    />
                    {t.popular}
                  </label>
                  <button className="primary-button" type="submit">
                    {t.saveItem}
                  </button>
                </form>
              </section>

              {profile.role === "owner" ? (
                <section>
                  <h3>{t.workerEditor}</h3>
                  <form className="admin-form" onSubmit={handleAddWorker}>
                    <label>
                      {t.username}
                      <input value={workerForm.username} onChange={(event) => setWorkerForm((current) => ({ ...current, username: event.target.value }))} />
                    </label>
                    <label>
                      {t.password}
                      <input value={workerForm.password} onChange={(event) => setWorkerForm((current) => ({ ...current, password: event.target.value }))} />
                    </label>
                    <label>
                      {t.fullName}
                      <input value={workerForm.full_name} onChange={(event) => setWorkerForm((current) => ({ ...current, full_name: event.target.value }))} />
                    </label>
                    <label>
                      {t.titleRu}
                      <input value={workerForm.title_ru} onChange={(event) => setWorkerForm((current) => ({ ...current, title_ru: event.target.value }))} />
                    </label>
                    <label>
                      {t.titleEn}
                      <input value={workerForm.title_en} onChange={(event) => setWorkerForm((current) => ({ ...current, title_en: event.target.value }))} />
                    </label>
                    <button className="primary-button" type="submit">
                      {t.addWorker}
                    </button>
                  </form>
                </section>
              ) : null}

              {feedback ? <p className="feedback-message">{feedback}</p> : null}
            </div>
          )}
        </aside>
      ) : null}
    </div>
  );
}

export default App;
